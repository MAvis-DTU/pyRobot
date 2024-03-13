Download NaoQI C++ SDK

Filename | md5 | link
--- | --- | ---
naoqi-sdk-2.5.5.5-linux64.tar.gz | 6168a4da3cabb1030ada3a99d954708e |https://community-static.aldebaran.com/resources/2.5.10/NAOqi%20SDK/naoqi-sdk-2.5.7.1-linux64.tar.gz
ctc-linux64-atom-2.5.2.74.zip | 82bff07795a2a4090b6b536a7ca5193e |https://community-static.aldebaran.com/resources/2.5.10/CTC/ctc-linux64-atom-2.5.10.7.zip

Extract the zips to the root folder with names `ctc-linux64-atom` and `naoqi-sdk`

Build Docker image
```
docker build -t pepper:pepper .
```

Start Docker container
```
docker run --rm -it -v (pwd):/pepper/ --entrypoint bash pepper:pepper
```
Note: Mounting volumes is probably a bit different on Windows.

In the docker container you can then build the executable using.
```
cd /pepper
mkdir -p build
cmake .. -DCMAKE_BUILD_TYPE=Release
make
```

Deploy to pepper using (replace with IP the that of the relevant robot)
```
scp pepper_cameras nao@192.168.1.108:/home/nao/pepper_cameras
```

You should now be able to SSH into the robot and run the execuable.
