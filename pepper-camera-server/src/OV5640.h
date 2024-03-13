#pragma once


#include <cstdint>
#include <linux/videodev2.h>

namespace OV5640 {

    struct Frame {
        uint8_t* data;
        uint32_t length;
    };

    struct Device;

    Device* initialize(const char* path, int camera_index);

    enum class Setting : uint32_t {
        Brightness = V4L2_CID_BRIGHTNESS,
        Contrast = V4L2_CID_CONTRAST,
        Saturation = V4L2_CID_SATURATION,
        WhiteBalanceAutomatic = V4L2_CID_AUTO_WHITE_BALANCE,
        ExposureAutomatic = V4L2_CID_EXPOSURE_AUTO,
        Exposure = V4L2_CID_EXPOSURE,
        GainAutomatic = V4L2_CID_AUTOGAIN,
        Gain = V4L2_CID_GAIN,
    };

    int32_t get_setting(Device* device, Setting setting);
    void set_setting(Device* device, Setting setting, int32_t value);

    void close(Device* cam);

    Frame fetch_frame(Device* cam);
}
