import os
import re
import time

import subprocess32 as subprocess

from hedroid.logger import logger


class XvfbExecutor(object):
    xdpyinfo_p = re.compile(r"unable to open display")

    def __init__(self, display, dpi, dim):
        self.display = display
        self.dpi = dpi
        self.dim = dim

        self._proc = None

    def xdpyinfo_wait(self):
        logger.debug('xdpyinfo wait')
        cmd = ["xdpyinfo", "-display", ":{}".format(self.port)]
        while True:
            output = subprocess.check_output(
                cmd, timeout=2, universal_newlines=True)
            for line in output.splitlines():
                if self.xdpyinfo_p.search(line):
                    break
            time.sleep(0.1)

    def start(self):
        logger.debug('Starting Xvfb executor')
        cmd = ["Xvfb", ":{}".format(self.display), "-dpi", str(self.dpi),
               "-screen", "0", self.dim, "-extension", "DAMAGE"]
        self._proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        # Wait till Xvfb properly starts up
        self.xdpyinfo_wait()
        return True

    def stop(self):
        logger.debug('Stopping Xvfb executor')
        try:
            self._proc.terminate()
        except:
            pass
        try:
            self._proc.kill()
        except:
            pass


class Xvfb(object):
    def __init__(self, display=None, dpi=560, dim='720x1280x24'):
        self.display = display or os.environ.get('DISPLAY_PORT', '1')
        self.dpi = dpi
        self.dim = dim

        self._executor = None

    def start(self):
        logger.debug('Starting Xvfb')

        self.executor = XvfbExecutor(self.display, self.dpi, self.dim)
        self.executor.start()
        logger.debug('Xvfb Ready!')

    def stop(self):
        logger.debug('Stopping Xvfb')
        self.executor.stop()


if __name__ == '__main__':
    xvfb = Xvfb()
    xvfb.start()
