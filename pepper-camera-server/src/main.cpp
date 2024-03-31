#include <opencv2/opencv.hpp>
#include <stdio.h>
#include <iostream>
#include <signal.h>
#include <unistd.h>
#include <arpa/inet.h>

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wdeprecated-declarations"
#pragma GCC diagnostic ignored "-Wignored-qualifiers"
#pragma GCC diagnostic ignored "-Wparentheses"
#pragma GCC diagnostic ignored "-Wunused-parameter"
#pragma GCC diagnostic ignored "-Wplacement-new="
#include <alcommon/albroker.h>
#include <alvision/alimage.h>
#include <alproxies/alvideodeviceproxy.h>
#include <alproxies/almemoryproxy.h>
#include <alproxies/alfacedetectionproxy.h>

#pragma GCC diagnostic pop

#include "OV5640.h"

struct CameraServer {
    OV5640::Device* device;
    int server_socket;
    std::atomic<bool> running;
    pthread_t worker;
};

void configure_camera(CameraServer* server) {
    OV5640::set_setting(server->device, OV5640::Setting::Brightness, 0);
    OV5640::set_setting(server->device, OV5640::Setting::Contrast, 32);
    OV5640::set_setting(server->device, OV5640::Setting::Saturation, 64);
    OV5640::set_setting(server->device, OV5640::Setting::WhiteBalanceAutomatic, 0);
    OV5640::set_setting(server->device, OV5640::Setting::GainAutomatic, 0);
    OV5640::set_setting(server->device, OV5640::Setting::Gain, 16);
    OV5640::set_setting(server->device, OV5640::Setting::ExposureAutomatic, 0);
    OV5640::set_setting(server->device, OV5640::Setting::Exposure, 1024);
}

void send_frame(CameraServer* server, int client_socket) {

    OV5640::Frame temp = OV5640::fetch_frame(server->device);
    cv::Mat frame_yuyv(480, 640, CV_8UC2, temp.data);
    cv::Mat frame_bgr;
    cv::cvtColor(frame_yuyv, frame_bgr, cv::COLOR_YUV2BGR_YUYV);

    std::vector<uint8_t> compressed_frame;
    std::vector<int32_t> compression_flags;
    compression_flags.push_back(cv::IMWRITE_JPEG_QUALITY);
    compression_flags.push_back(45);

    cv::imencode(".jpg", frame_bgr, compressed_frame, compression_flags);

    uint32_t image_size = compressed_frame.size();
    send(client_socket, &image_size, sizeof(uint32_t), 0);

    // Send the actual message
    send(client_socket, compressed_frame.data(), image_size, 0);
}

void* camera_worker_thread(void* raw) {
    auto server = (CameraServer*) raw;
    while (server->running) {
        sockaddr_in client_address;
        socklen_t client_addr_len = sizeof(client_address);
        int client_socket = accept(server->server_socket, reinterpret_cast<struct sockaddr*>(&client_address), &client_addr_len);
        if (client_socket == -1) {
            std::cerr << "Error accepting connection\n";
            continue;
        }

        std::cout << "Client connected from " << inet_ntoa(client_address.sin_addr) << ":" << ntohs(client_address.sin_port) << std::endl;

        send_frame(server, client_socket);

        // Close the client socket
        close(client_socket);
    }
    return nullptr;
}

void startup_camera_server(CameraServer* server, const char* path, int id, int port) {

    // Create a socket
    server->server_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (server->server_socket == -1) {
        std::cerr << "Error creating socket\n";
        exit(EXIT_FAILURE);
    }

    // Set up the server address structure
    sockaddr_in server_address;
    server_address.sin_family = AF_INET;
    server_address.sin_addr.s_addr = INADDR_ANY;
    server_address.sin_port = htons(port);  // Choose any available port
    int opt = 1;

    // Set socket option
    if (setsockopt(server->server_socket, SOL_SOCKET, SO_REUSEADDR, (char *)&opt, sizeof(opt)) < 0) {
        std::cerr << "Error setting socket option\n";
        close(server->server_socket);
        exit(EXIT_FAILURE);
    }

    // Bind the socket to the address
    if (bind(server->server_socket, reinterpret_cast<struct sockaddr*>(&server_address), sizeof(server_address)) == -1) {
        std::cerr << "Error binding socket\n";
        close(server->server_socket);
        exit(EXIT_FAILURE);
    }

    // Listen for incoming connections
    if (listen(server->server_socket, 5) == -1) { // allow 5 requests to queue up
        std::cerr << "Error listening for connections\n";
        close(server->server_socket);
        exit(EXIT_FAILURE);
    }

    printf("Server listening on port %d...\n", port);

    server->running = true;
    server->device = OV5640::initialize(path, id);
    configure_camera(server);
    pthread_create(&server->worker, nullptr, camera_worker_thread, server);
}


void shutdown_camera_server(CameraServer* server) {
    server->running = false;
    pthread_join(server->worker, nullptr);
    close(server->server_socket);
    OV5640::close(server->device);
}

std::atomic<bool> running;

void sig_handler(int signo)
{
  if (signo == SIGINT)
    running = false;
}

// Function to be called when a client connects
void process_request(int clientSocket) {
    // Replace this with your actual data or processing logic
    const char* message = "Hello, client!";

    // Calculate the length of the message
    size_t messageLength = strlen(message);

    // Send the length as a 4-byte integer (network byte order)
    uint32_t lengthToSend = htonl(static_cast<uint32_t>(messageLength));
    send(clientSocket, &lengthToSend, sizeof(lengthToSend), 0);

    // Send the actual message
    send(clientSocket, message, messageLength, 0);
}

int main(int argc, const char** argv) {

    bool forward_camera_enabled = false;
    bool down_camera_enabled = true;

    boost::shared_ptr<AL::ALBroker> broker = AL::ALBroker::createBroker("LocalBroker", "0.0.0.0", 54000, "127.0.0.1", 9559);

    //Unsubscribe all NaoQi modules, such that we can claim the raw hardware interfaces
    AL::ALVideoDeviceProxy al_video;
    std::vector<std::string> subs = al_video.getSubscribers();
    for (auto &sub : subs) {
        al_video.unsubscribe(sub);
    }

    // Determine robot version since there are slight differences in the camera hardware
    AL::ALMemoryProxy al_mem;
    std::string version = al_mem.getData("RobotConfig/Body/BaseVersion");
    printf("Robot version: %s\n", version.c_str());

    // Find version specific paths to camera devices
    int forward_cam_path_id;
    int forward_cam_device_id;
    int down_cam_path_id;
    int down_cam_device_id;

    if (version == "1.8") {
        forward_cam_path_id = 1;
        forward_cam_device_id = 0;
        down_cam_path_id = 2;
        down_cam_device_id = 0;
    } else if (version == "1.8A") {
        forward_cam_path_id = 0;
        forward_cam_device_id = 0;
        down_cam_path_id = 1;
        down_cam_device_id = 1;
    } else {
        printf("Unsupported robot version!\n");
        printf("Please add support in onboard_cameras/Cameras.cpp!\n");
        std::exit(-1);
    }


    CameraServer forward_cam;
    CameraServer down_cam;

    if (forward_camera_enabled) {
	auto forward_path = "/dev/video" + std::to_string(forward_cam_path_id);
        startup_camera_server(&forward_cam, forward_path.c_str(), forward_cam_device_id, 12345);
    }

    if (down_camera_enabled) {
	auto down_path = "/dev/video" + std::to_string(down_cam_path_id);
        startup_camera_server(&down_cam, down_path.c_str(), down_cam_device_id, 12346);
    }

    // AL::ALTrackerProxy al_tracker;
    // al_tracker.stopTracker();
    // al_tracker.unregisterAllTargets();
    // al_tracker.registerTarget("Face", 0.1);
    // al_tracker.setMode("WholeBody");
    // al_tracker.track("Face");
    // printf("Tracker started\n");
    
    // Do the thing
    printf("Starting\n");
    signal(SIGINT, sig_handler);
    running = true;
    while (running) {
        usleep(10000);
    }
    printf("Stopping\n");

    // Shutdown
    if (forward_camera_enabled) shutdown_camera_server(&forward_cam);
    if (down_camera_enabled) shutdown_camera_server(&down_cam);
}

