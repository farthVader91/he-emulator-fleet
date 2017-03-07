import os

from hedroid.logger import logger
from hedroid.common_settings import VAR_DIR


class Executor(object):
    def __init__(self, id):
        self.id = id
        self._proc = None

        self.stdout_fd = None

    def _start(self):
        raise NotImplementedError()

    def start(self):
        logger.debug('Starting {}'.format(self.__class__.__name__))
        self.stdout_fd = open(
            os.path.join(
                VAR_DIR, "{}-{}".format(
                    self.__class__.__name__, self.id)), 'w')
        self._proc = self._start()

    def stop(self):
        logger.debug('Stopping {}'.format(self.__class__.__name__))
        try:
            self._proc.terminate()
        except:
            pass
        try:
            self._proc.kill()
        except:
            pass
        # Really wait for child process to terminate
        self._proc.wait()
        # Prevents zombie processes
        del self._proc
        self._proc = None
        # Close file descriptor
        self.stdout_fd.close()
