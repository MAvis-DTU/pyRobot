import socket
import msgpack
import time
import math
import sys

"""
Using the robot agent type differs from previous agent types.
  - Firstly, install additional package 'msgpack'.
    Use pip for installation, like this: 
        'python -m pip install numpy msgpack'. 
    Exact steps may vary based on your platform and Python 
    installation. 

  - Secondly, you don't need the Java server for the robot. So, the command
    to start the search client in the terminal is different, for example:
        'python searchclient/searchclient.py -robot -ip 192.168.0.102 -level levels/SAsoko1_04.lvl'
    runs the searchclient with the 'robot' agent type on the robot at IP 192.168.0.102.

  - To connect to the robots, connect to the Pepper hotspot. To reduce
    the load on the hotspot, please disconnect between your sessions.
    
  - A good starting point is using something similar to the 'classic' agent type and then
    replacing it with calls to the 'robot' interface.
"""

# for linux and mac
# export PYTHONPATH=${PYTHONPATH}:/home/seb/Downloads/python-sdk/lib/python2.7/site-packages


def degrees(degree):
    '''
    :param degree: angle in degrees  
    :return: angle in radians
    '''
    return degree * (math.pi / 180)

# Robot Client Class for use with the robot server class
class RobotClient():
    def __init__(self, ip):
        self.ip = ip

        # Base port number for all robots off of ip address
        if self.ip == '192.168.1.102':
            port = 5001  # if port fails you have from 5000-5009
        elif self.ip == '192.168.1.105':
            port = 5010  # if port fails you have from 5010-5019
        elif self.ip == '192.168.1.106':
            port = 5020 # if port fails you have from 5020-5029
        elif self.ip == '192.168.1.108':
            port = 5030 # if port fails you have from 5030-5039

        self.host = socket.gethostname()  # as both code is running on same pc
        self.port = port  # socket server port number

        self.client_socket = socket.socket()  # instantiate
        self.client_socket.connect((self.host, self.port))  # connect to the server

        self.direction_mapping = { 'Move(N)': 90,
                        'Move(E)': 0,
                        'Move(S)': 270,
                        'Move(W)': 180,
                        'Push(N,N)': 90,
                        'Push(E,E)': 0,
                        'Push(S,S)': 270,
                        'Push(W,W)': 180}

    def forward(self,distance,block):
        forward_cmd = {
            'type': 'forward',
            'distance': float(distance),
            'block': block
        }
        message = msgpack.packb(forward_cmd, use_bin_type=True)
        self.client_socket.send(message)
        data = self.client_socket.recv(1024).decode() 
    
    def say(self, s):
        say_cmd = {
            'type': 'say',
            'sentence': s
        }
        message = msgpack.packb(say_cmd, use_bin_type=True)
        self.client_socket.send(message)  # send message
        data = self.client_socket.recv(1024)

    def turn(self,angle,block):
        turn_cmd = {
            'type': 'turn',
            'angle': float(angle),
            'block': block
        }
        message = msgpack.packb(turn_cmd, use_bin_type=True)
        self.client_socket.send(message)
        data = self.client_socket.recv(1024)

    
    def stand(self):
        stand_cmd = {
            'type': 'stand'
        }
        message = msgpack.packb(stand_cmd, use_bin_type=True)
        self.client_socket.send(message)
        data = self.client_socket.recv(1024)

    def shutdown(self):
        shutdown_cmd = {
            'type': 'shutdown'
        }
        message = msgpack.packb(shutdown_cmd, use_bin_type=True)
        self.client_socket.send(message)
        data = self.client_socket.recv(1024)

    def move(x,y,theta,block):
        move_cmd = { 
            'type': 'move',
            'x': float(x),
            'y': float(y),
            'theta': float(theta),
            'block': block
        }
        message = msgpack.packb(move_cmd, use_bin_type=True)
        self.client_socket.send(message)
        data = self.client_socket.recv(1024)

    def close(self):
        if self.client_socket:
            self.client_socket.close()

    '''
        OBS:
        The functions below do not call the server, but are used to convert the plan to a list of commands that 
        can then be sent to the server.

    '''
    
    def face_direction(self,current_direction, target_direction):
        '''
        :param degree: current direction of the robot in degrees
        :return: turns robot to face the target direction in the shortest route, and returns the new direction
        '''

        # Facing east respective to the map is direction 0.
        # Make the robot turn to the desired angle via. the shortest route
        d = (target_direction - current_direction + 540) % 360 - 180

        # turn robot
        robot.turn(degrees(d), block=True)

        # corrects for the position of base of the robot. 
        if current_direction != target_direction:
            robot.forward(0.03,block=True)

        return target_direction
    
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
    
    def listen(self, duration=3, channels=[0,0,1,0],playback=False):

        '''
        :param duration: duration of the recording in seconds
        :param channels: list of 4 booleans indicating which channels (microphones) to record [left, right, front, back]
        :param playback: boolean indicating whether to play back the recording after recording
        '''

        listen_cmd = {
            'type': 'listen',
            'duration': duration,
            'channels': channels,
            'playback': playback
        }
        message = msgpack.packb(listen_cmd, use_bin_type=True)
        self.client_socket.send(message)
        #TODO: Check how to get data stream back from server
        data = self.client_socket.recv(1024)



if __name__ == '__main__':
    ip = sys.argv[1]

    # connect to the server and robot
    robot = RobotClient(ip)

    # test the robots listening
    #robot.listen(3, playback=True)

    # test the robots speech
    robot.stand()

    #robot.say('I am executing plan. Please watch out!')
    time.sleep(5)

    # set the robots initial direction
    current_direction = robot.direction_mapping['Move(S)']

    # test-plan
    plan = ['Move(W)', 'Move(S)', 'Move(E)','Move(N)']

    # execute the plan
    for action in plan:

        # The robot will announce which way it is going
        #robot.declare_direction(action)

        # Compute and turn to the correct direction wrt. plan and update directions
        target_direction = robot.face_direction(current_direction, robot.direction_mapping[action])
        current_direction = target_direction
        
        # Move forward (distance equal to cell). 
        if 'Push' in action:
            # This can change depending on robot and box
            robot.forward(0.55, block=True)
            robot.forward(-0.07, block=True)
        else:
            robot.forward(0.50, block=True)

    # Make robot announce that it is done with the plan!
    # robot.say('I am done executing the plan. Thank you for watching!')
    robot.stand()

    # close the connection to the robot server
    robot.close()


