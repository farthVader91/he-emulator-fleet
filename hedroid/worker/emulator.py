import re
import os
import time

import subprocess32 as subprocess

from hedroid.logger import logger
from hedroid.worker.utils import parse_manifest, download_to_temp
from hedroid.worker.executor import Executor


class EmulatorExecutor(Executor):
    def __init__(self, port, avd, display, **kwargs):
        super(EmulatorExecutor, self).__init__(port)
        self.port = port
        self.avd = avd
        self.display = display

    def adb_wait(self):
        logger.debug('Adb shell wait')
        cmd = ["adb", "-s", "emulator-{}".format(self.port),
               "wait-for-device"]
        return subprocess.check_call(cmd, timeout=20)

    def sys_boot_wait(self):
        logger.debug('Sys boot wait')
        cmd = ["adb", "-s", "emulator-{}".format(self.port),
               "shell", "getprop", "sys.boot_completed"]
        pattern = re.compile(r"1")
        while True:
            output = subprocess.check_output(
                cmd, universal_newlines=True)
            if pattern.match(output):
                break
            time.sleep(0.1)

    def _start(self):
        # Set DISPLAY variable first
        env = os.environ.copy()
        if self.display:
            env['DISPLAY'] = ':{}'.format(self.display)
        cmd = ["emulator", "-port", self.port, "-avd", self.avd,
               "-no-boot-anim", "-nojni", "-netfast", "-gpu", "swiftshader",
               "-qemu", "-enable-kvm"]
        if os.getenv("NO_WINDOW"):
            cmd.append("-no-window")
        proc = subprocess.Popen(
            cmd,
            env=env,
            stdout=self.stdout_fd,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        # Wait till boot
        logger.debug(self.adb_wait())
        self.sys_boot_wait()
        return proc


class Emulator(object):
    def __init__(self, port=None, avd=None, display=None):
        self.port = port or os.environ.get('ADB_PORT', '5554')
        self.avd = avd or os.environ.get('AVD_NAME', 'nexus6-android7')
        self.display = display

        self.executor = None
        self.last_package_maniphest = None

    def start(self):
        logger.debug('Starting emulator')

        self.executor = EmulatorExecutor(self.port, self.avd, self.display)
        self.executor.start()
        logger.debug('Emulator ready!')

    def _install_apk(self, path):
        logger.debug('Install apk {}'.format(path))
        cmd = ["adb", "-s", "emulator-{}".format(self.port),
               "install", "-r", path]
        output = subprocess.check_output(
            cmd, timeout=15, universal_newlines=True)
        if re.match(r"Success", output):
            logger.debug('Finished installing apk')
            return True

    def uninstall_package(self, package):
        logger.debug('Uninstalling package: {}'.format(package))
        cmd = ["adb", "-s", "emulator-{}".format(self.port),
               "uninstall", package]
        output = subprocess.check_output(cmd, timeout=15)
        if re.match(r"Success", output):
            logger.debug('Finished uninstalling apk')
            return True

    def install_apk(self, path):
        if self.last_package_maniphest is not None:
            self.uninstall_package(self.last_package_maniphest['package'])
        output = self._install_apk(path)
        self.last_package_maniphest = parse_manifest(path)
        return output

    def install_apk_from_url(self, url):
        download_to = download_to_temp(url)
        return self.install_apk(download_to)

    def start_package_activity(self, package, activity):
        cmd = ["adb", "-s", "emulator-{}".format(self.port),
               "shell", "am", "start", "-n",
               "{}/{}".format(package, activity)]
        subprocess.check_call(cmd, timeout=5)
        logger.debug('Started package activity')
        # TODO: Check if activity was really started
        return True

    def start_last_package(self):
        if self.last_package_maniphest is None:
            raise Exception('No package installed previously')
        return self.start_package_activity(**self.last_package_maniphest)

    def cleanup(self):
        # Uninstall last installed package
        if self.last_package_maniphest is not None:
            package = self.last_package_maniphest['package']
            self.uninstall_package(package)
        # TODO: Goto Home screen
        logger.debug('You are yet to implement "GOTO HOMESCREEN"')
        return True

    def stop(self):
        logger.debug('Stopping emulator')
        self.executor.stop()


if __name__ == '__main__':
    em = Emulator()
    em.start()
    em.install_apk("/home/vishal/Downloads/apks/com.utorrent.client.apk")
