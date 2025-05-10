import paramiko
import time
from paramiko.ssh_exception import SSHException

class SSHTerminal:
    def __init__(self):
        self.hostn = None
        self.connected = False
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self, hostn, usern, password):
        try:
            self.ssh.connect(hostn, username=usern, password=password)
            self.shell = self.ssh.invoke_shell()
            self.hostn = hostn
            self.connected = True
            output = self.shell.recv(1024).decode()
            print(output.strip())
            print(f"Connected to {hostn}")
            self.strt()
        except SSHException as e:
            print(f"Failed to connect to {hostn} : error: {e}")

    def strt(self):
        if not self.connected:
            print("SSH connection not established")
            return

        while True:
            cmd = input(" ")
            if cmd.strip().startswith("exit"):
                self.disconnect()
                break
            else:
                self.run_command(cmd)

    def run_command(self, cmd):
        try:
            self.shell.send(cmd + "\n")
            time.sleep(0.2)
            output = self.shell.recv(1024).decode()
            print(output.strip())

        except SSHException as e:
            print(f"Failed to execute {cmd} : {e}")

    def disconnect(self):
        if not self.connected or self.ssh.get_transport() is None:
            print("SSH connection not established")
            return

        self.ssh.close()
        self.connected = False

if __name__ == "__main__":
    ssh = SSHTerminal()
    hostn = input("hostn: ")
    usrn = input("username: ")
    passwd = input("password: ")
    ssh.connect(hostn, usrn, passwd)