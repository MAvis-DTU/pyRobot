# from test_call import *
import subprocess


def connectPepper(ip, filename):
    subprocess.run(['python2', f'{filename}'], input=bytes(ip, encoding="utf-8"), stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)


ip = '192.168.1.108'
connectPepper(ip, 'test_call.py')
