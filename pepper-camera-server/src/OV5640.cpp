#include "OV5640.h"

#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#include <fcntl.h>

#include <unistd.h>
#include <sys/mman.h>
#include <sys/ioctl.h>

#include <linux/videodev2.h>
#include <opencv2/opencv.hpp>

namespace OV5640 {

    void fail(const char* msg) {
        fprintf(stderr, "%s\n", msg);
        exit(-1);
    }

    int xioctl(int fd, int request, void* arg) {
        int ret;
        int retries = 3;

        do  {
            ret = ioctl(fd, request, arg);
        } while (retries-- > 0 && ret == -1 && errno == EINTR);

        return ret;
    }

#define V4L2_MODE_VIDEO 0x0002
#define VIDEO_BUFFER_COUNT 4

    struct v4l2_buffer_t {
        void* start;
        size_t length;
    };

    struct Device {
        int fd;
        v4l2_buffer_t* buffers;
        uint32_t buffer_count;
        Frame result_buffer;
    };



    Device* initialize(const char* path, int camera_index) {

        auto cam = (Device*) malloc(sizeof(Device));

        cam->fd = open(path, O_RDWR | O_NONBLOCK);

        v4l2_input input = {};
        input.index = camera_index;
        if (xioctl(cam->fd, VIDIOC_ENUMINPUT, &input) == -1) {
            fail("Failed to enumerate input");
        }
        if (xioctl(cam->fd, VIDIOC_S_INPUT, &input.index) == -1) {
            fail("Failed to set input");
        }

        v4l2_streamparm params = {};

        params.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        params.parm.capture.capturemode = V4L2_MODE_VIDEO;
        params.parm.capture.timeperframe.numerator = 1;
        params.parm.capture.timeperframe.denominator = 30;
        if (xioctl(cam->fd, VIDIOC_S_PARM, &params) == -1) {
            fail("Failed to set video stream parameters");
        }

        uint32_t width = 640;
        uint32_t height = 480;

        v4l2_format fmt = {};
        fmt.fmt.pix.width = width;
        fmt.fmt.pix.height = height;
        fmt.fmt.pix.field = V4L2_FIELD_NONE;
        fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        //For some reason, it is ONLY possible to capture the cameras
        //native YUV (4:2:2) [Y,U,Y,V] format. Others spew strange errors
        fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_YUYV;

        if (xioctl(cam->fd, VIDIOC_TRY_FMT, &fmt) == -1) {
            printf("Failed trying to set pixel format\n");
        }

        if (fmt.fmt.pix.width != width && fmt.fmt.pix.height != height) {
            width = fmt.fmt.pix.width;
            height = fmt.fmt.pix.height;
            printf("Frame size adjusted to: %dx%d pixels\n", width, height);
        }

        if (xioctl(cam->fd, VIDIOC_S_FMT, &fmt) == -1) {
            printf("Failed to set pixel format\n");
        }


        v4l2_requestbuffers req = {};
        req.count = VIDEO_BUFFER_COUNT;
        req.memory = V4L2_MEMORY_MMAP;
        req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        if (xioctl(cam->fd, VIDIOC_REQBUFS, &req) == -1) {
            fail("Failed to request video buffers");
        }
        if (req.count != VIDEO_BUFFER_COUNT) {
            fail("Insufficient buffer memory");
        }
        cam->buffer_count = req.count;

        cam->buffers = (v4l2_buffer_t*) calloc(req.count, sizeof(v4l2_buffer_t));
        if (!cam->buffers) {
            fail("Failed to allocate buffer memory");
        }

        v4l2_buffer buf = {};
        for (uint32_t i = 0; i < req.count; i++) {
            memset(&buf, 0, sizeof(v4l2_buffer));
            buf.index = i;
            buf.memory = V4L2_MEMORY_MMAP;
            buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
            if (xioctl(cam->fd, VIDIOC_QUERYBUF, &buf) == -1) {
                fail("Failed to query buffer");
            }
            cam->buffers[i].length = buf.length;
            cam->buffers[i].start = mmap(nullptr, buf.length, PROT_READ | PROT_WRITE, MAP_SHARED, cam->fd, buf.m.offset);
            if (cam->buffers[i].start == MAP_FAILED) {
                fail("Failed to setup mmap buffer");
            }
        }

        cam->result_buffer.length =  640*480*2;
        cam->result_buffer.data = (uint8_t*) malloc(cam->result_buffer.length);

        for (uint32_t i = 0; i < req.count; i++) {
            memset(&buf, 0, sizeof(v4l2_buffer));
            buf.index = i;
            buf.memory = V4L2_MEMORY_MMAP;
            buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;

            if (xioctl(cam->fd, VIDIOC_QBUF, &buf) == -1) {
                fail("Failed to queue buffer");
            }
        }

        v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        if (xioctl(cam->fd, VIDIOC_STREAMON, &type) == -1) {
            fail("Failed to start the video stream");
        }

        return cam;
    }

    int get_setting(Device* cam, Setting setting) {
        v4l2_control ctrl;
        ctrl.id = (uint32_t) setting;
        xioctl(cam->fd, VIDIOC_G_CTRL, &ctrl);
        return ctrl.value;
    }

    void set_setting(Device* cam, Setting setting, int32_t value) {
        v4l2_control ctrl;
        ctrl.id = (uint32_t) setting;
        ctrl.value = value;
        auto ret = xioctl(cam->fd, VIDIOC_G_CTRL, &ctrl);
        if (ret == 1) {
            printf("Error setting camera setting %u\n", (uint32_t) setting);
        }
    }

    void close(Device* cam) {
        v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        if (xioctl(cam->fd, VIDIOC_STREAMOFF, &type) == -1) {
            fail("Failed to turn off the video stream");
        }

        for (uint32_t i = 0; i < cam->buffer_count; i++) {
            munmap(cam->buffers[i].start, cam->buffers[i].length);
        }

        ::close(cam->fd);
    }

    Frame fetch_frame(Device* cam) {

        fd_set fds;
        timeval tv = {};

        int status = 1;
        while (status > 0) {
            FD_ZERO(&fds);
            FD_SET(cam->fd, &fds);

            tv.tv_sec = 1;
            tv.tv_usec = 0;

            status = select(cam->fd+1, &fds, nullptr, nullptr, &tv);

            if (status == -1) {
                if (errno == EINTR) {
                    status = 1; //Just an interrupt. Try again
                    continue;
                }
                fail("Failed to select frame");
            }
            break;
        }

        if (status <= 0) {
            fail("Invalid sensor reading");
        }

        v4l2_buffer buf;

        buf.memory = V4L2_MEMORY_MMAP;
        buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        if (xioctl(cam->fd, VIDIOC_DQBUF, &buf) == -1) {
            fail("Failed to retrieve frame");
        }

        auto current_buf = &cam->buffers[buf.index];
        memcpy(cam->result_buffer.data, current_buf->start, 640*480*2);

        if (xioctl(cam->fd, VIDIOC_QBUF, &buf) == -1) {
            fail("Failed to requeue buffer");
        }

        return cam->result_buffer;

    }
}
