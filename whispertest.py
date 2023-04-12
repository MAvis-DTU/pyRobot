from robot_client import *
import whisper
import os
import time

# connect to robot
robot = RobotClient('192.168.1.102')

# Load the model
model = whisper.load_model('base')

while True:
    # Peper
    robot.say('which way should I go?')

    time.sleep(2)
    # Transcribe the audio file
    robot.listen(2)


    # Get the transcription
    text = model.transcribe(str(os.getcwd())+"/tmp/test.wav")['text'].lower()
    print(text)

    # works fast if model is loaded
    # if north in, then go 
    if 'north' in text:
        robot.forward(1, block=True) # move forward 1 meter
    elif 'south' in text:
        robot.forward(-1, block=True)
    if 'east' in text:
        robot.turn(degrees(90), block=True)
        robot.forward(1, block=True)
    if 'west' in text:
        robot.turn(degrees(-90), block=True)
        robot.forward(1, block=True)