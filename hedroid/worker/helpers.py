import os

from hedroid.worker.zk_droid import DroidZkClient
from hedroid.logger import logger
from hedroid.worker.xvfb import Xvfb
from hedroid.worker.emulator import Emulator
from hedroid.worker.vnc import X11VNC
from hedroid.worker.websockify import Websockify


class Droid(object):
    def __init__(self, xvfb, emulator, x11vnc, websockify):
        self.xvfb = xvfb
        self.emulator = emulator
        self.x11vnc = x11vnc
        self.websockify = websockify

    def start(self):
        logger.debug('Starting droid')
        started = []
        try:
            self.xvfb.start()
            started.append(self.xvfb)
            self.emulator.start()
            started.append(self.emulator)
            self.x11vnc.start()
            started.append(self.x11vnc)
            self.websockify.start()
            started.append(self.websockify)
            logger.debug('Droid ready!')
        except:
            logger.error('Failed to start droid. Reverting')
            for proc in started:
                try:
                    proc.stop()
                except:
                    pass

    def stop(self):
        logger.debug('Stopping droid')
        to_stop = [self.websockify, self.x11vnc, self.emulator, self.xvfb]
        for proc in to_stop:
            try:
                proc.stop()
            except:
                pass
        logger.debug('Droid stopped!')


class DroidBuilder(object):
    def __init__(self):
        self.port = os.environ.get('ADB_PORT', '5554')
        self.avd = os.environ.get('AVD_NAME', 'nexus6-android7')
        self.display = os.environ.get('DISPLAY_PORT', '1')
        self.dpi = 560
        self.dim = '720x1280x24'
        self.clip = '530x965+15+30'
        self.ws_port = 6080

    def set_port(self, port):
        self.port = port
        return self

    def set_avd(self, avd):
        self.avd = avd
        return self

    def set_display(self, display):
        self.display = display
        return self

    def set_dpi(self, dpi):
        self.dpi = dpi
        return self

    def set_dim(self, dim):
        self.dim = dim
        return self

    def set_clip(self, clip):
        self.clip = clip
        return self

    def set_ws_port(self, port):
        self.ws_port = port
        return self

    def build(self):
        xvfb = Xvfb(
            display=self.display,
            dpi=self.dpi,
            dim=self.dim,
        )
        emulator = Emulator(
            port=self.port,
            avd=self.avd,
            display=self.display,
        )
        x11vnc = X11VNC(
            display=self.display,
            clip=self.clip,
        )
        websockify = Websockify(
            source_port=self.ws_port,
            target_port=x11vnc.get_rfbport(),
        )
        # Finally build droid
        droid = Droid(
            xvfb=xvfb,
            emulator=emulator,
            x11vnc=x11vnc,
            websockify=websockify,
        )
        return droid


class DroidCoordinator(object):
    def __init__(self):
        self.droids_to_start = []
        self.initialised = {}

    def add_droid(self, droid):
        self.droids_to_start.append(droid)

    def start_droid(self, droid):
        droid.start()
        zk_client = DroidZkClient()
        zk_client.setup()
        self.initialised[zk_client.nodename] = {
            'droid': droid,
            'zk_client': zk_client,
        }

    def setup(self):
        while True:
            try:
                droid = self.droids_to_start.pop()
                self.start_droid(droid)
            except IndexError:
                break

    def count(self):
        return len(self.initialised)

    def get_droid(self, id):
        return self.initialised[id]['droid']

    def get_zk_client(self, id):
        return self.initialised[id]['zk_client']

    def stop_droid(self, id):
        # Stop Zk client
        zk_client = self.get_zk_client(id)
        zk_client.teardown()
        # Stop droid
        droid = self.get_droid(id)
        droid.stop()

    def iter_droid_ids(self):
        return self.initialised.iterkeys()

    def teardown(self):
        for instance_id in self.iter_droid_ids():
            self.stop_droid(instance_id)
