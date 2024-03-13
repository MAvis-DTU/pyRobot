cmake_minimum_required(VERSION 3.5 FATAL_ERROR)
project(pepper-camera-server)

include(FindPackageHandleStandardArgs)

#Compiler configuration

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -g -m32 -static-libstdc++ -D_GLIBCXX_USE_CXX11_ABI=0 -pthread")
set(CMAKE_LD_FLAGS "${CMAKE_LD_FLAGS} -m32")

#Dependencies

set(NAOQI_INCLUDE_PATH ${CMAKE_SOURCE_DIR}/naoqi-sdk/include)

set(NAOQI_LIB_SEARCH_PATH ${CMAKE_SOURCE_DIR}/ctc-linux64-atom)

set(CMAKE_INSTALL_RPATH
        ${NAOQI_LIB_SEARCH_PATH}/boost/lib
        ${NAOQI_LIB_SEARCH_PATH}/libnaoqi/lib
        ${NAOQI_LIB_SEARCH_PATH}/openssl/lib
        ${NAOQI_LIB_SEARCH_PATH}/systemd/lib
        ${NAOQI_LIB_SEARCH_PATH}/icu/lib
        ${NAOQI_LIB_SEARCH_PATH}/zlib/lib
        ${NAOQI_LIB_SEARCH_PATH}/xz_utils/lib
        )

set(NAOQI_LIBRARIES
        ${NAOQI_LIB_SEARCH_PATH}/icu/lib/libicudata.so
        ${NAOQI_LIB_SEARCH_PATH}/icu/lib/libicui18n.so
        ${NAOQI_LIB_SEARCH_PATH}/icu/lib/libicuio.so
        ${NAOQI_LIB_SEARCH_PATH}/icu/lib/libicule.so
        ${NAOQI_LIB_SEARCH_PATH}/icu/lib/libiculx.so
        ${NAOQI_LIB_SEARCH_PATH}/icu/lib/libicutest.so
        ${NAOQI_LIB_SEARCH_PATH}/icu/lib/libicutu.so
        ${NAOQI_LIB_SEARCH_PATH}/icu/lib/libicuuc.so
        ${NAOQI_LIB_SEARCH_PATH}/systemd/lib/libgudev-1.0.so
        ${NAOQI_LIB_SEARCH_PATH}/systemd/lib/libnss_myhostname.so.2
        ${NAOQI_LIB_SEARCH_PATH}/systemd/lib/libsystemd-daemon.so
        ${NAOQI_LIB_SEARCH_PATH}/systemd/lib/libsystemd-id128.so
        ${NAOQI_LIB_SEARCH_PATH}/systemd/lib/libsystemd-journal.so
        ${NAOQI_LIB_SEARCH_PATH}/systemd/lib/libsystemd-login.so
        ${NAOQI_LIB_SEARCH_PATH}/systemd/lib/libsystemd.so
        ${NAOQI_LIB_SEARCH_PATH}/systemd/lib/libudev.so
        ${NAOQI_LIB_SEARCH_PATH}/xz_utils/lib/liblzma.so
        ${NAOQI_LIB_SEARCH_PATH}/zlib/lib/libz.so
        ${NAOQI_LIB_SEARCH_PATH}/openssl/lib/libcrypto.so
        ${NAOQI_LIB_SEARCH_PATH}/openssl/lib/libssl.so
        ${NAOQI_LIB_SEARCH_PATH}/libnaoqi/lib/libalproxies.so
        ${NAOQI_LIB_SEARCH_PATH}/libnaoqi/lib/libalcommon.so
        ${NAOQI_LIB_SEARCH_PATH}/libnaoqi/lib/libalvalue.so
        ${NAOQI_LIB_SEARCH_PATH}/libqi/lib/libqi.so
        ${NAOQI_LIB_SEARCH_PATH}/bzip2/lib/libbz2.so
        ${NAOQI_LIB_SEARCH_PATH}/tbb/lib/libtbb.so
        ${NAOQI_LIB_SEARCH_PATH}/tbb/lib/libtbbmalloc.so
        ${NAOQI_LIB_SEARCH_PATH}/jpeg/lib/libjpeg.so
        ${NAOQI_LIB_SEARCH_PATH}/png/lib/libpng.so
        ${NAOQI_LIB_SEARCH_PATH}/tiff/lib/libtiff.so
        ${NAOQI_LIB_SEARCH_PATH}/ffmpeg/lib/libavcodec.so
        ${NAOQI_LIB_SEARCH_PATH}/ffmpeg/lib/libavutil.so
        ${NAOQI_LIB_SEARCH_PATH}/ffmpeg/lib/libavdevice.so
        ${NAOQI_LIB_SEARCH_PATH}/ffmpeg/lib/libavfilter.so
        ${NAOQI_LIB_SEARCH_PATH}/ffmpeg/lib/libswscale.so
        ${NAOQI_LIB_SEARCH_PATH}/ffmpeg/lib/libavformat.so
        ${NAOQI_LIB_SEARCH_PATH}/opus/lib/libopus.so
        ${NAOQI_LIB_SEARCH_PATH}/speex/lib/libspeex.so
        ${NAOQI_LIB_SEARCH_PATH}/ogg/lib/libogg.so
        ${NAOQI_LIB_SEARCH_PATH}/libtheora/lib/libtheoradec.so
        ${NAOQI_LIB_SEARCH_PATH}/libtheora/lib/libtheoraenc.so
        ${NAOQI_LIB_SEARCH_PATH}/libtheora/lib/libtheora.so
        ${NAOQI_LIB_SEARCH_PATH}/vo-aacenc/lib/libvo-aacenc.so
        ${NAOQI_LIB_SEARCH_PATH}/vo-amrwbenc/lib/libvo-amrwbenc.so
        ${NAOQI_LIB_SEARCH_PATH}/opencore-amr/lib/libopencore-amrwb.so
        ${NAOQI_LIB_SEARCH_PATH}/opencore-amr/lib/libopencore-amrnb.so
        ${NAOQI_LIB_SEARCH_PATH}/vorbis/lib/libvorbis.so
        ${NAOQI_LIB_SEARCH_PATH}/vorbis/lib/libvorbisenc.so
        ${NAOQI_LIB_SEARCH_PATH}/v4l/lib/libv4l1.so
        ${NAOQI_LIB_SEARCH_PATH}/v4l/lib/libv4l2.so
        ${NAOQI_LIB_SEARCH_PATH}/v4l/lib/libv4lconvert.so
        ${NAOQI_LIB_SEARCH_PATH}/opencv2/lib/libopencv_core.so
        ${NAOQI_LIB_SEARCH_PATH}/opencv2/lib/libopencv_imgproc.so
        ${NAOQI_LIB_SEARCH_PATH}/opencv2/lib/libopencv_contrib.so
        ${NAOQI_LIB_SEARCH_PATH}/opencv2/lib/libopencv_highgui.so
        ${NAOQI_LIB_SEARCH_PATH}/boost/lib/libboost_system.so)

#List of modules
include_directories(${NAOQI_INCLUDE_PATH})


add_executable(pepper_cameras src/main.cpp src/OV5640.cpp)
target_link_libraries(pepper_cameras ${NAOQI_LIBRARIES})
