import subprocess
import threading
import time
import signal
import sys
import socket
from io import TextIOWrapper
from contextlib import contextmanager
import os
from ..config.config import WATCHDOG_INTERVAL_MS
from ..log.log import debugf, infof, errorf, watchdog

class WatchDog:
    def __init__(self, port: int, command: list):
        self.port = port
        self.command = command
        self.stdout_r, self.stdout_w = None, None
        self.stderr_r, self.stderr_w = None, None
        self.ctx = None
        self.cancel = None
        self.wait_group = threading.Event()
        self.has_check_health = False
        self.is_starting = False
        self.init()

    def init(self):
        if self.ctx is None:
            self.ctx, self.cancel = contextmanager(lambda: (yield))()

        if self.stdout_r is None or self.stdout_w is None:
            self.stdout_r, self.stdout_w = TextIOWrapper(subprocess.PIPE), TextIOWrapper(subprocess.PIPE)

        if self.stderr_r is None or self.stderr_w is None:
            self.stderr_r, self.stderr_w = TextIOWrapper(subprocess.PIPE), TextIOWrapper(subprocess.PIPE)

    def check_port(self) -> bool:
        if self.port == 0:
            errorf("watchdog port is not set")
            return False

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.1)
            result = s.connect_ex(('localhost', self.port))
            if result != 0:
                debugf("check port error, %s", result)
                return False
            return True

    def check_health_loop(self):
        debugf("start checkHealthLoop")
        if self.has_check_health:
            debugf("checkHealthLoop has started, skip")
            return

        self.has_check_health = True
        self.wait_group.set()

        ticker = threading.Event()
        while not ticker.wait(WATCHDOG_INTERVAL_MS / 1000):
            if self.is_starting:
                continue

            if not self.check_port():
                retry = 5
                should_restart = True
                while retry > 0:
                    debugf("port is not available, waiting...")
                    retry -= 1
                    time.sleep(WATCHDOG_INTERVAL_MS / 1000)
                    if self.check_port():
                        should_restart = False
                        break

                if should_restart:
                    debugf("port is not available, try to restart")
                    err = self.start()
                    if err is not None:
                        errorf("WatchDog check health failed, and try to restart failed: %s", err)
                        self.kill_self()

        self.has_check_health = False
        self.wait_group.clear()
        debugf("stop checkHealthLoop")

    def start(self) -> None:
        debugf("start watchdog")
        if not self.command or len(self.command) == 0:
            return ValueError("command is not set")

        if self.is_starting:
            infof("WatchDog is starting...")
            return

        self.init()
        self.is_starting = True

        infof("command: %s", " ".join(self.command))
        proc = subprocess.Popen(self.command, stdout=self.stdout_w, stderr=self.stderr_w, text=True)

        threading.Thread(target=self.read_output_loop, args=(self.stdout_r,)).start()
        threading.Thread(target=self.read_output_loop, args=(self.stderr_r,)).start()

        infof("WatchDog is starting progress, waiting port available")

        while True:
            time.sleep(WATCHDOG_INTERVAL_MS / 1000)
            debugf("pid %d, waiting port available...", proc.pid)

            if self.check_port():
                break

        infof("port is available, start checkhealth")

        if not self.has_check_health:
            threading.Thread(target=self.check_health_loop).start()

        self.is_starting = False
        debugf("start watchdog finished")

    def read_output_loop(self, r: TextIOWrapper):
        self.wait_group.wait()

        for line in r:
            line = line.strip()
            if line:
                watchdog(line)

    def stop(self):
        infof("WatchDog stop")
        if self.cancel:
            self.cancel()

    def wait_stop(self):
        self.wait_group.wait()

    def kill_self(self):
        self.stop()
        self.wait_stop()
        infof("WatchDog kill self")
        os.kill(os.getpid(), signal.SIGTERM)

def new_watchdog(port: int, command: list) -> WatchDog:
    w = WatchDog(port, command)
    w.init()
    return w