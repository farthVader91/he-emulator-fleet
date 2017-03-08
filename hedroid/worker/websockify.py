import os
import time

import subprocess32 as subprocess

from hedroid.logger import logger
from hedroid.common_settings import CONFIG_DIR, DEBUG
from hedroid.worker.executor import Executor


class WebsockifyExecutor(Executor):
    def __init__(self, source_port, target_port):
        super(WebsockifyExecutor, self).__init__(source_port)
        self.source_port = source_port
        self.target_port = target_port

    def netcat_wait(self, proc):
        logger.debug('Netcat wait')
        cmd = ["nc", "-w", "2", "-zv", "localhost", str(self.source_port)]
        while True:
            try:
                subprocess.check_call(cmd)
            except subprocess.CalledProcessError:
                time.sleep(0.1)
            else:
                break

    def _start(self):
        cmd = ["websockify"]
        if not DEBUG:
            cmd = ["websockify",
                   "--cert", os.path.join(CONFIG_DIR, "hackerearth.crt"),
                   "--key", os.path.join(CONFIG_DIR, "hackerearth.key"),
                   "--ssl-only"]

        cmd.extend([":{}".format(self.source_port),
                    ":{}".format(self.target_port)])
        proc = subprocess.Popen(
            cmd,
            stdout=self.stdout_fd,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        # Wait till websockify process is ready
        self.netcat_wait(proc)
        return proc


class Websockify(object):
    def __init__(self, source_port=None, target_port=None):
        self.source_port = source_port or os.environ.get('WS_PORT', 6080)
        self.target_port = target_port or (
            5900 + os.environ.get('DISPLAY_PORT', 1))

        self.executor = None

    def start(self):
        logger.debug('Starting websockify')

        self.executor = WebsockifyExecutor(self.source_port, self.target_port)
        self.executor.start()
        logger.debug('Websockify Ready!')

    def stop(self):
        logger.debug('Stopping Websockify')
        self.executor.stop()


if __name__ == '__main__':
    websockify = Websockify()
    websockify.start()
