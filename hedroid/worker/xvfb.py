import os
import re
import time

import subprocess32 as subprocess

from hedroid.logger import logger
from hedroid.worker.executor import Executor
from hedroid.common_settings import VAR_DIR


class XvfbExecutor(Executor):
    xdpyinfo_p = re.compile(r"unable to open display")

    def __init__(self, display, dpi, dim):
        super(XvfbExecutor, self).__init__(display)
        self.display = display
        self.dpi = dpi
        self.dim = dim

    def xdpyinfo_wait(self):
        logger.debug('xdpyinfo wait')
        cmd = ["xdpyinfo", "-display", ":{}".format(self.display)]
        while True:
            output = subprocess.check_output(
                cmd, timeout=1, universal_newlines=True)
            if not self.xdpyinfo_p.search(output):
                break
            time.sleep(0.1)

    def _start(self):
        cmd = ["Xvfb", ":{}".format(self.display), "-dpi", str(self.dpi),
               "-screen", "0", self.dim, "-extension", "DAMAGE"]
        proc = subprocess.Popen(
            cmd,
            stdout=self.stdout_fd,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        # Wait till Xvfb properly starts up
        self.xdpyinfo_wait()
        return proc


class Xvfb(object):
    def __init__(self, display=None, dpi=560, dim='720x1280x24'):
        self.display = display or os.environ.get('DISPLAY_PORT', '1')
        self.dpi = dpi
        self.dim = dim

        self.executor = None

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
