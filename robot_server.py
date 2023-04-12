import socket
import msgpack
import sys
import os
import naoqi
import time

from scp import SCPClient
import paramiko

from scipy.io.wavfile import write
from threading import Thread

"""
Using the robot agent type differs from previous agent types.
  - Firstly, install additional packages 'scp' and 'msgpack'.
    Use pip for installation, like this: 
        'python2 -m pip install numpy msgpack'. 
    Exact steps may vary based on your platform and Python 
    installation. Installing 'scp' also installs the 'paramiko' package.

  - Secondly, you don't need the Java server for the robot - although you can. So, the command
    to start the search client in the terminal is different, for example:
        'python searchclient/searchclient.py -robot -ip 192.168.1.102 -level levels/SAsoko1_04.lvl'
    runs the searchclient with the 'robot' agent type on the robot at IP 192.168.1.102.

  - To connect to the robots, connect to the Pepper hotspot. To reduce
    the load on the hotspot, please disconnect between your sessions.
    
  - A good starting point is using something similar to the 'classic' agent type and then
    replacing it with calls to the 'robot' interface.
"""


# for linux and mac
# export PYTHONPATH=${PYTHONPATH}:/home/seb/Downloads/python-sdk/lib/python2.7/site-packages



class RealRobot:
    def __init__(self, ip):
        self.ip = ip

        # Connect to robot to retrieve files from robot (scp)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_system_host_keys()
        
        if self.ip == '192.168.1.102':
            ssh.connect(hostname=self.ip, username="nao", password="salt")
        elif self.ip == '192.168.1.105)':
            ssh.connect(hostname=self.ip, username="nao", password="pepper")
        elif self.ip == '192.168.1.106)':
            ssh.connect(hostname=self.ip, username="nao", password="r2dtu")
        elif self.ip == '192.168.1.108)':
            ssh.connect(hostname=self.ip, username="nao", password="Sokrates1")

        self.scp = SCPClient(ssh.get_transport())

        # Standard ALProxies
        self.tts = naoqi.ALProxy("ALTextToSpeech", ip, 9559)
        self.motion = naoqi.ALProxy("ALMotion", ip, 9559)
        self.behavior = naoqi.ALProxy("ALBehaviorManager", ip, 9559)
        self.tracker = naoqi.ALProxy("ALTracker", ip, 9559)
        self.posture = naoqi.ALProxy("ALRobotPosture", ip, 9559)
        self.mem = naoqi.ALProxy("ALMemory", ip, 9559)
        self.session = self.mem.session()
        self.mem = self.session.service("ALMemory")
        self.asr = naoqi.ALProxy("ALSpeechRecognition", ip, 9559)
        self.leds = naoqi.ALProxy("ALLeds", ip, 9559)
        self.video = naoqi.ALProxy("ALVideoDevice", ip, 9559)
        self.recorder = naoqi.ALProxy("ALAudioRecorder", ip, 9559)
        self.player = naoqi.ALProxy("ALAudioPlayer", ip, 9559)
        self.tablet = naoqi.ALProxy("ALTabletService", ip, 9559)
        self.system = naoqi.ALProxy("ALSystem", ip, 9559)
        self.pm = naoqi.ALProxy("ALPreferenceManager", ip, 9559)
        self.touch = naoqi.ALProxy("ALTouch", ip, 9559)


        # Setting collision protection False (will interfere with motion based ALProxies if True)
        self.motion.setExternalCollisionProtectionEnabled("Move", False)
        self.motion.setExternalCollisionProtectionEnabled("Arms", False)

        # Wake up robot (if not already up) and go to standing posture)
        self.motion.wakeUp()
        self.posture.goToPosture("Stand", 0.5)

    def download_file(self, file_name):
        """
        Download a file from robot to ./tmp folder in root.
        ..warning:: Folder ./tmp has to exist!
        :param file_name: File name with extension (or path)
        :type file_name: string
        """
        self.scp.get(file_name, local_path="/tmp/")
        print("[INFO]: File " + file_name + " downloaded")
        self.scp.close()

    def say(self, sentence, language="English"):
        Thread(target=(
            lambda: self.tts.say(sentence) if language == "English" else self.tts.say(sentence, language))).start()

    def forward(self, dist, block = False):
        if block == False:
            Thread(target=(lambda: self.motion.moveTo(dist, 0, 0))).start()
        else:
            self.motion.moveTo(dist, 0, 0)

    def turn(self, dist, block=False):

        if block == False:
            Thread(target=(lambda: self.motion.moveTo(0, 0, dist))).start()
        else:
            self.motion.moveTo(0, 0, dist)

    def stand(self):
        self.posture.goToPosture("Stand", 0.5)

    def offLeds(self,leds="AllLeds"):
        robot.leds.off(leds)

    def onLeds(self,leds="AllLeds"):
        robot.leds.on(leds)

    def declare_direction(self, move):
        direction = {'Move(N)': "I am going North",
                     'Move(E)': 'I am going East',
                     'Move(S)': 'I am going South',
                     'Move(W)': 'I am going West',
                     'Push(N,N)': 'I am pushing North',
                     'Push(E,E)': 'I am pushing East',
                     'Push(S,S)': 'I am pushing South',
                     'Push(W,W)': 'I am pushing West'}
        return robot.say(direction[move])

    def sensor_touched(self, sensor):

        # Get list of sensor_status in the form of a list: [['Head', False, []], ['LArm', False, []], ... ]]
        sensor_list = robot.touch.getStatus()

        # Create sensor dictionary to get sensor info
        sensor_dict = {     'Head': 0,
                            'LArm': 1,
                            'Leg': 2,
                            'RArm': 3,
                            'LHand': 4,
                            'RHand': 5,
                            'Bumper/Back': 6,
                            'Bumper/FrontLeft': 7,
                            'Bumper/FrontRight': 8,
                            'Head/Touch/Front': 9,
                            'Head/Touch/Middle': 10,
                            'Head/Touch/Rear': 11,
                            'LHand/Touch/Back': 12,
                            'RHand/Touch/Back': 13,
                             'Base': 14
                            }

        # Return the boolean value of the sensor: True if touched, False if untouched
        return sensor_list[sensor_dict[sensor]][1]
    
    def listen(self, duration=3, channels = [0,0,1,0],playback=False):
        # start recording
        robot.recorder.startMicrophonesRecording("/home/nao/test.wav", "wav", 16000,[0,0,1,0])
        print('Started recording')

        # wait for duration
        time.sleep(duration)

        # stop recording
        robot.recorder.stopMicrophonesRecording()

        # load the file
        print('Done recording')
        fileId = robot.player.loadFile("/home/nao/test.wav")

        
        # play the file if playback is True
        if playback:
            print('playing sound first')
            robot.player.play(fileId)

        
        # Get the audio data but do not pass through socket. 
        # Instead save it locally for faster speech to text!
        self.scp.get('test.wav', local_path=str(os.getcwd())+"/tmp/")
        print("[INFO]: File " + 'test.wav' + " downloaded to " + str(os.getcwd())+"/tmp/")
        self.scp.close()
    

    
    def command(self, data):
        #tested
        if data['type'] == 'say':
                self.say(str(data['sentence']))

        #tested
        if data['type'] == 'forward':
            self.forward(float(data['distance']),bool(data['block']))

        #not tested
        if data['type'] == 'turn':
            self.turn(float(data['angle']),bool(data['block']))

        #not tested
        if data['type'] == 'stand':
            self.stand()

        #not tested
        if data['type'] == 'shutdown':
            self.shutdown()
        
        if data['type'] == 'listen':
            self.listen(float(data['duration']),data['channels'],bool(data['playback']))


def server_program(robot):
    # Get the hostname
    host = socket.gethostname()

    # Base port number for all robots off of ip address
    if robot.ip == '192.168.1.102':
        port = 5001  # if port fails you have from 5000-5009
    elif robot.ip == '192.168.1.105':
        port = 5010  # if port fails you have from 5010-5019
    elif robot.ip == '192.168.1.106':
        port = 5020 # if port fails you have from 5020-5029
    elif robot.ip == '192.168.1.108':
        port = 5030 # if port fails you have from 5030-5039

    server_socket = socket.socket()  # get instance
    # Look closely. The bind() function takes tuple as argument
   
    server_socket.bind((host, port))  # bind host address and port together

    # Ronfigure how many client the server can listen simultaneously
    server_socket.listen(1)
    conn, address = server_socket.accept()  # accept new connection

    print("Connection from: " + str(address))

    while True:
        # Receive data stream. it won't accept data packet greater than 1024 bytes

        data = conn.recv(1024)

        # check if we have package waiting
        if not data:
            # if data is not received break
            break

        # Unpack bytes into data dict
        data = msgpack.unpackb(data, raw=False)

        # Execute command from data dict
        robot.command(data)

        # or try this if you want to use the class
        # robot.command(data)

        #print the data we got from client
        print("from connected user: " + str(data))

        # send data to the client socket
        data = 'Server got ran command ' + str(data['type'])

        #send data back to client
        conn.send(data.encode())  

    conn.close()  # close the connection


if __name__ == '__main__':
    # get the ip address of the robot
    ip = sys.argv[1]

    # create a robot object and pass the ip address
    robot = RealRobot(ip)

    # start the server that converts the commands (Python 3.x) to robot commands (Python 2.7)
    server_program(robot)
