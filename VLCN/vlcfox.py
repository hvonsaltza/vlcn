import socket
import subprocess
import time


class VLC:
    def __init__(self,filepath):
        self.SCREEN_NAME = 'vlc'
        self.HOST = 'localhost'
        self.PORT = 8888
        
        cmd = subprocess.Popen([filepath,'--rc-host=localhost:8888'], shell=True)
        time.sleep(3)
        self.SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SOCK.connect((self.HOST, self.PORT))

    def x(self, cmd):
        '''Prepare a command and send it to VLC'''
        if not cmd.endswith('\n'):
            cmd = cmd + '\n'
        cmd = cmd.encode()
        self.SOCK.sendall(cmd)

    def pause(self):
        self.x('pause')

    def play(self):
        self.x('play')

    def stop(self):
        self.x('stop')

    def prev(self):
        self.x('prev')

    def next(self):
        self.x('next')

    def add(self, path):
        self.x('add %s'  % (path,))

    def enqueue(self, path):
        self.x('enqueue %s' % (path,))

    def clear(self):
        self.x('clear')

    def shutdown(self):
        self.x('shutdown')

    def fullscreen(self):
        self.x('f on')

    def seek(self, time):
        self.x('seek %s' % (time,))
