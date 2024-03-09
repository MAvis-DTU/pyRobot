import qi
import sys

# session = qi.Session()
# session.connect("tcp://192.168.1.108:9559")
# # ip = input()
# # session.connect(f"tcp://{ip}:9559")
# tts = session.service("ALTextToSpeech")
# tts.say("Hello Big Boi!")
#

import qi
import argparse
# from naoqi import ALProxy


def main(robotIP, PORT, message):

    session = qi.Session()
    # # ip = raw_input()
    session.connect(f"tcp://{robotIP}:{PORT}")
    motionProxy = session.service("ALMotion")
    postureProxy = session.service("ALRobotPosture")
    ttsProxy = session.service("ALTextToSpeech")
    motionProxy.wakeUp()

    postureProxy.goToPosture("StandInit", 0.5)

    ttsProxy.say(message)
    motionProxy.rest()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="192.168.1.108", help="Robot IP address.")
    parser.add_argument("--port", type=int, default=9559, help="Robot port number.")
    parser.add_argument("--message", type=str, default="Hello Big Boi!", help="Message to say.")
    args = parser.parse_args()
    main(args.ip, args.port, args.message)