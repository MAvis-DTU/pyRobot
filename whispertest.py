from robot_client import *
import whisper
import os
import time

# connect to robot
robot = RobotClient('192.168.1.102')

# Load the model
model = whisper.load_model('base')

initial = True
while True:
    # Peper
    if initial == True:
        robot.say('What do you want me to do?')
        initial = False
    else: 
        robot.say('What about now?')

    time.sleep(2)
    
    # Transcribe the audio file
    robot.listen(2)

    # Get the transcription
    text = model.transcribe(str(os.getcwd())+"/tmp/test.wav")['text'].lower()
    print(text)

    # works fast if model is loaded
    # if north in, then go 
    if 'forward' in text:
        robot.forward(1, block=True) 

    elif 'back' in text:
        robot.forward(-1, block=True) 

    elif 'go left' in text:
        robot.turn(degrees(90), block=True) 
        robot.forward(1, block=True)

    elif 'go right' in text:
        robot.turn(degrees(-90), block=True) 
        robot.forward(1, block=True)

    elif 'shut down' or 'shutdown' or 'turn off' in text: 
        robot.say('Goodbye')
        robot.shutdown()

    elif 'turn left' in text: 
        robot.turn(degrees(90), block=True)

    elif 'turn right' in text:
        robot.turn(degrees(-90), block=True)