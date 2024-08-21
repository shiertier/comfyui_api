import subprocess
import threading
import time
import signal
import socket
import os
from ..config import WATCHDOG_INTERVAL_MS, START_HOST
from .log import debugf, infof, errorf, watchdog

class WatchDog:
    def __init__(self, host: str, port: int, command: list):
        self.host = host
        self.port = port
        self.command = command
        self.process = None
        self.has_check_health = False
        self.is_starting = False
        self.stop_event = threading.Event()
        self.stdout_r, self.stderr_r = None, None

    def check_port(self) -> bool:
        '''检测端口是否占用'''
        if self.port == 0:
            errorf("WatchDog port is not set", "WatchDog 端口未设置")
            return False

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.1)
            result = sock.connect_ex((self.host, self.port))
            if result != 0:
                debugf("{} {} is not available: {}".format(self.host, self.port, result), "{} {} 不可用: {}".format(self.host, self.port, result))
                return False
            return True

    def check_health_loop(self):
        # 健康检查
        debugf("Starting health check loop", "开始健康检查循环")
        if self.has_check_health:
            debugf("Health check loop already running, skipping", "健康检查循环已经运行，跳过")
            return

        self.has_check_health = True

        while not self.stop_event.wait(WATCHDOG_INTERVAL_MS / 1000):
            if self.is_starting:
                continue

            if not self.check_port():
                debugf("Port {} is not available, trying to restart".format(self.port), "端口 {} 不可用，尝试重启".format(self.port))
                for _ in range(5):
                    time.sleep(WATCHDOG_INTERVAL_MS / 1000)
                    if self.check_port():
                        break
                else:
                    if self.start() is not None:
                        errorf("Failed to restart process after health check", "健康检查后重启进程失败")
                        self.kill_self()

        self.has_check_health = False
        debugf("Health check loop stopped", "健康检查循环已停止")

    def start(self) -> None:
        """启动进程"""
        debugf("Starting WatchDog", "启动 WatchDog")

        if not self.command:
            #raise ValueError("Command is not set")
            return "Command is not set"

        if self.is_starting:
            infof("WatchDog is already starting...", "WatchDog 已经在启动中...")
            return

        try:
            self.is_starting = True
            infof("Command: {}".format(" ".join(self.command)), "命令: {}".format(" ".join(self.command)))

            self.process = subprocess.Popen(
                self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            self.stdout_r, self.stderr_r = self.process.stdout, self.process.stderr

            threading.Thread(target=self.read_output_loop, args=(self.stdout_r,)).start()

            infof("Process started with PID: {}".format(self.process.pid), "进程已启动, PID: {}".format(self.process.pid))

            while not self.check_port():
                time.sleep(WATCHDOG_INTERVAL_MS / 1000)
                debugf("PID {}: Waiting for port {}".format(self.process.pid, self.port), "PID {}: 等待端口 {}".format(self.process.pid, self.port))

            infof("Port {} is available, starting health check".format(self.port), "端口 {} 可用, 开始健康检查".format(self.port))

            if not self.has_check_health:
                threading.Thread(target=self.check_health_loop).start()

            self.is_starting = False
            debugf("WatchDog started", "WatchDog 已启动")
        except Exception as e:
            errorf("Error starting WatchDog: {}".format(e), "启动 WatchDog 时出错: {}".format(e))
            return e

    def read_output_loop(self, pipe):
        for line in iter(pipe.readline, ''):
            if line.strip():
                watchdog(line.strip())
        pipe.close()

    def stop(self):
        infof("Stopping WatchDog", "停止 WatchDog")
        self.stop_event.set()
        if self.process:
            self.process.terminate()

    def wait_stop(self):
        self.stop_event.wait()

    def kill_self(self):
        self.stop()
        self.wait_stop()
        infof("WatchDog terminating", "WatchDog 已终止")
        os.kill(os.getpid(), signal.SIGTERM)

def new_watchdog(port: int, command: list) -> WatchDog:
    return WatchDog(port, command)