from hedroid.logger import logger


class Droid(object):
    def __init__(self, xvfb, emulator, x11vnc, websockify):
        self.xvfb = xvfb
        self.emulator = emulator
        self.x11vnc = x11vnc
        self.websockify = websockify

    def start(self):
        logger.debug('Starting droid')
        self.xvfb.start()
        self.emulator.start()
        self.x11vnc.start()
        self.websockify.start()

    def stop(self):
        logger.debug('Stopping droid')
        self.websockify.stop()
        self.x11vnc.stop()
        self.emulator.stop()
        self.xvfb.stop()
