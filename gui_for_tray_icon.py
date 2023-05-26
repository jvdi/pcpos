import pystray, webbrowser
from PIL import Image


# TrayIcon for show app is run
class TrayIcon():
    def __init__(self):
        self.image = Image.open('assets/pos.ico')
        self.menu = (
            pystray.MenuItem('درباره نرم افزار', lambda: webbrowser.open('https://github.com/jvdi/rahkar-pcpos')),
            pystray.MenuItem('بستن سرویس', lambda: [self.stop()])
            )
        self.icon = pystray.Icon('PCPosAPI', self.image, 'PCPosAPI is running', self.menu)

    def run_detached(self):
        self.icon.run_detached()

    def stop(self):
        self.icon.stop()