import logging
import os
import subprocess
import socket
import threading
import time
import signal
from contextlib import contextmanager

from ..config import WATCHDOG_INTERVAL_MS
from .log import errorf, infof, debugf, watchdog

class WatchDog:
    def __init__(self, port, command):
        self.port = port
        self.command = command
        self.stdout_r, self.stdout_w = os.pipe()
        self.stderr_r, self.stderr_w = os.pipe()
        self.has_check_health = False
        self.is_starting = False
        self.stop_event = threading.Event()
        self.thread = None

    def check_port(self):
        if self.port == 0:
            errorf("watchdog port is not set")
            return False

        try:
            with socket.create_connection(("localhost", self.port), timeout=0.1):
                return True
        except Exception as e:
            debugf("check port error, %s", e)
            return False

    def check_health_loop(self):
        debugf("start checkHealthLoop")
        try:
            if self.has_check_health:
                debugf("checkHealthLoop has started, skip")
                return

            self.has_check_health = True
            while not self.stop_event.is_set():
                time.sleep(config.WatchDogIntervalMs / 1000)
                if self.is_starting:
                    continue

                if not self.check_port():
                    retry = 5
                    should_restart = True
                    while retry > 0:
                        debugf("port is not available, waiting...")
                        retry -= 1
                        time.sleep(config.WatchDogIntervalMs / 1000)
                        if self.check_port():
                            should_restart = False
                            break

                    if should_restart:
                        debugf("port is not available, try to restart")
                        try:
                            self.start()
                        except Exception as e:
                            errorf("WatchDog check health failed, and try to restart failed: %s", e)
                            self.kill_self()
        finally:
            debugf("stop checkHealthLoop")
            self.has_check_health = False

    def start(self):
        debugf("start watchdog")
        if not self.command:
            raise ValueError("command is not set")

        if self.is_starting:
            infof("WatchDog is starting...")
            return

        self.is_starting = True
        try:
            infof("command: %s", ' '.join(self.command))
            self.process = subprocess.Popen(self.command, stdout=self.stdout_w, stderr=self.stderr_w, preexec_fn=os.setsid)
            self.thread = threading.Thread(target=self.read_output_loop)
            self.thread.start()
            infof("WatchDog is starting progress, waiting port available")

            while not self.check_port():
                time.sleep(config.WatchDogIntervalMs / 1000)
                debugf("pid %d, waiting port available...", self.process.pid)

            infof("port is available, start checkhealth")

            if not self.has_check_health:
                health_thread = threading.Thread(target=self.check_health_loop)
                health_thread.start()
        finally:
            self.is_starting = False

    def read_output_loop(self):
        with os.fdopen(self.stdout_r, 'r') as stdout, os.fdopen(self.stderr_r, 'r') as stderr:
            while not self.stop_event.is_set():
                line = stdout.readline()
                if line:
                    line = line.strip()
                    if line:
                        watchdog(line)

    def stop(self):
        infof("WatchDog stop")
        self.stop_event.set()
        if self.process:
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)

    def wait_stop(self):
        if self.thread:
            self.thread.join()

    def kill_self(self):
        self.stop()
        self.wait_stop()
        infof("WatchDog kill self")
        os.kill(os.getpid(), signal.SIGTERM)

@contextmanager
def watch_dog_context(port, command):
    wd = WatchDog(port, command)
    try:
        yield wd
    finally:
        wd.kill_self()
