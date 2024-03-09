import qi
import time
import argparse
import sys
import time
from PIL import Image
import almath
import keyboard

def remove_all_subscribers(video_service):
    """
    Remove all subscribers from the video service.
    """
    # Get the list of current subscribers
    subscribers = video_service.getSubscribers()
    # Unsubscribe all current subscribers
    for subscriber in subscribers:
        video_service.unsubscribe(subscriber)

# Create a flag to indicate when to end the stream
end_stream = False
    
def main(session, stand=True, headtilt=10.0):
    """
    First get an image, then show it on the screen with PIL.
    """
    if stand:
        posture = session.service("ALRobotPosture")
        try:
            posture.goToPosture("Stand", 0.5)
        except (EOFError):
            print("Standard stand failed...")
    motion_service = session.service("ALMotion")

    # Tilt the head slightly down
    try:
        motion_service.setStiffnesses("Head", 1.0)
        # Example showing multiple trajectories
        names      = ["HeadYaw", "HeadPitch"]
        angleLists = [0.0*almath.TO_RAD, headtilt*almath.TO_RAD]
        timeLists  = [1.0, 1.2]
        isAbsolute = True
        motion_service.angleInterpolation(names, angleLists, timeLists, isAbsolute)
        print('Tilting head...')
    except (EOFError):
        print("Tilting head failed...")

    # Get the service ALVideoDevice.
    video_service = session.service("ALVideoDevice")
    remove_all_subscribers(video_service)
    resolution = 1    # VGA 0: 160*120 1: 320*240 2: 640*480
    colorSpace = 11   # RGB
    # Use mouth camera
    video_service.setActiveCamera(1)
    # Capture image
    videoClient = video_service.subscribe("python_client", resolution, colorSpace, 30)

    # Function to set end_stream to True when 's' key is pressed
    def on_key_event(event):
        global end_stream
        if event.name == 's':
            end_stream = True

    # Subscribe to key events
    keyboard.on_press(on_key_event)
    frame_counter = 0
    start_time = time.time()
    try:
        while not end_stream:           
            t0 = time.time()
            # Get a camera image.
            naoImage = video_service.getImageRemote(videoClient)
            t1 = time.time()
            frame_counter += 1

            # Time the image transfer.
            print("Acquisition delay: ", t1 - t0)
            if (time.time() - start_time) >= 1:
                fps = frame_counter / (time.time() - start_time)
                print('FPS: ', fps)

                # Reset the frame counter and the initial time
                frame_counter = 0
                start_time = time.time()
            # Get the image size and pixel array.
            imageWidth = naoImage[0]
            imageHeight = naoImage[1]
            print(imageWidth, imageHeight)
            array = naoImage[6]
            image_string = str(bytearray(array))

            # Create a PIL Image from our pixel array.
            im = Image.frombytes("RGB", (imageWidth, imageHeight), image_string)

            # Save image
            im.save("camImage.png", "PNG")
            # Display the image.
            # im.show()

    finally:
        # Unsubscribe from key events
        keyboard.unhook_all()
        # Unsubscribe from video stream
        video_service.unsubscribe(videoClient)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="192.168.1.108",
                        help="Robot IP address.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")
    parser.add_argument("--stand", action='store_true', help="Stand the robot up.")
    parser.add_argument("--headtilt", type=float, default=10.0, help="Tilt the head down by this angle in degrees.")

    args = parser.parse_args()
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    main(session, stand=args.stand, headtilt=args.headtilt)
