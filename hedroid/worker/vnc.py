import os
import time

import subprocess32 as subprocess

from hedroid.logger import logger
from hedroid.common_settings import VAR_DIR
from hedroid.worker.executor import Executor


class X11VNCExecutor(Executor):
    def __init__(self, display, rfb_port, clip):
        super(X11VNCExecutor, self).__init__(display)
        self.display = display
        self.rfb_port = rfb_port
        self.clip = clip

        self._portfile_p = os.path.join(VAR_DIR, "vnc-port-{}".format(display))

    def portfile_wait(self):
        logger.debug('port file wait')
        retries = 0
        while True:
            if retries > 10:
                msg = 'Could not start x11vnc @ {}. Check the logs.'.format(
                    self.display)
                raise Exception(msg)
            if os.path.exists(self._portfile_p):
                break
            time.sleep(0.5)
            retries += 1

    def _start(self):
        cmd = ["x11vnc", "-forever", "-rfbport", str(self.rfb_port),
               "-display", ":{}".format(self.display),
               "-noxfixes", "-nowf", "-ncache", "10",
               "-clip", self.clip, "-flag", self._portfile_p]
        # Remove portfile if it previously exists
        try:
            os.remove(self._portfile_p)
        except:
            pass
        proc = subprocess.Popen(
            cmd,
            stdout=self.stdout_fd,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        # Wait till vnc server starts up completely
        self.portfile_wait()
        return proc

    def stop(self):
        # Delete port file on shutdown
        super(X11VNCExecutor, self).stop()
        try:
            os.remove(self._portfile_p)
        except:
            pass


class X11VNC(object):
    def __init__(self, display=None, clip=None):
        self.display = display or os.environ.get('DISPLAY_PORT', '1')
        self.clip = clip or '530x965+15+30'

        self.executor = None

    def get_rfbport(self):
        return 5900 + int(self.display)

    def start(self):
        logger.debug('Starting X11VNC')

        self.executor = X11VNCExecutor(self.display, self.get_rfbport(), self.clip)
        self.executor.start()
        logger.debug('X11VNC Ready!')

    def stop(self):
        logger.debug('Stopping X11VNC')
        self.executor.stop()


if __name__ == '__main__':
    x11vnc = X11VNC()
    x11vnc.start()
