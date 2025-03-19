import paramiko
import time
from paramiko.ssh_exception import SSHException


class SSHTerminal:
    def __init__(self):
        self.hostn = None
        self.connected = False
        self.ssh = paramiko.SSHClient()

    def connect(self, hostn, usern, password):
        try:
            self.ssh.connect(hostn, username=usern, password=password)
            self.shell = self.ssh.invoke_shell()
            self.hostn = hostn
            self.strt()
        except SSHException as e:
            print(f"Failed to connect to {hostn} : error: {e}")

    def strt(self):
        if not self.connected:
            print("SSH connection not established")
            return

        while True:
            cmd = input(f"{self.hostn}:> ")
            if cmd.strip().startswith("exit"):
                self.disconnect()

    def run_command(self, cmd):
        try:
            self.shell.send(cmd + "\n")
            time.sleep(0.5)
            output = self.shell.recv(1024).decode()

        except SSHException as e:
            print(f"Failed to execute {cmd} : {e}")


    def disconnect(self):
        if not self.connected:
            print("SSH connection not established")
            return

        self.ssh.close()
        self.connected = False



