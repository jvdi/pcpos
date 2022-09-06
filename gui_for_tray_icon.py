import pystray
from PIL import Image


# TrayIcon for show app is run
class TrayIcon():
    def __init__(self):
        self.image = Image.open('assets/pos.ico')
        self.icon = pystray.Icon('PCPosAPI', self.image, 'PCPosAPI is running', None)

    def run_detached(self):
        self.icon.run_detached()

    def stop(self):
        self.icon.stop()
        exit()
