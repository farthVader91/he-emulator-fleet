import re
import os
import time

from mirakuru import Executor, OutputExecutor, SimpleExecutor

from logger import logger


class AdbWaitExecutor(Executor):
    def pre_start_check(self):
        return False

    def after_start_check(self):
        return not self.running()


class EmulatorExecutor(Executor):
    def __init__(self, command, port, **kwargs):
        super(EmulatorExecutor, self).__init__(command, **kwargs)
        self.port = port

    def pre_start_check(self):
        return False

    def after_start_check(self):
        logger.debug('Adb shell wait')
        adb_wait_cmd = ["adb", "-s", "emulator-{}".format(self.port),
                        "wait-for-device"]
        AdbWaitExecutor(adb_wait_cmd, timeout=15).start()

        pattern = re.compile(r"1")
        sysb_wait_cmd = ["adb", "-s", "emulator-{}".format(self.port),
                         "shell", "getprop", "sys.boot_completed"]

        logger.debug('Sys boot wait')

        while True:
            e = SimpleExecutor(sysb_wait_cmd)
            e.start()
            line = e.output().readline()
            if pattern.match(line):
                break
            time.sleep(0.1)

        return True


class Emulator(object):
    def __init__(self, port=None, avd=None):
        self.port = port or os.environ.get('ADB_PORT', '5554')
        self.avd = avd or os.environ.get('AVD_NAME', 'nexus6-android7')
        self._proc = None

    def start(self):
        logger.debug('Starting emulator')
        cmd = ["emulator", "-port", self.port, "-avd", self.avd,
               "-no-boot-anim", "-nojni", "-netfast", "-no-window"]
        proc = EmulatorExecutor(cmd, port=self.port)
        proc.start()
        logger.debug('Emulator ready!')
        self._proc = proc

    def install_apk(self, path):
        logger.debug('Install apk {}'.format(path))
        cmd = ["adb", "-s", "emulator-{}".format(self.port),
               "install", "-r", path]
        OutputExecutor(cmd, banner=r"Success").start()
        return True

    def stop(self):
        logger.debug('Stopping emulator')
        self._proc.stop()


if __name__ == '__main__':
    em = Emulator()
    em.start()
    em.install_apk("/home/vishal/Downloads/apks/com.utorrent.client.apk")
