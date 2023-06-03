import base64
import os
import socket
import ssl
from getpass import getpass
from pathlib import Path
from letter import MailCreator
from file import File
from SMTPError import SMTPError


class Client:
    def __init__(self, login_from: str, to: str, subject: str, is_ssl: bool, do_auth: bool, do_verbose: bool,
                 directory: str, server_port: str):

        self.login_from = login_from
        self.to = to
        self.subject = subject
        self.is_ssl = is_ssl
        self.do_auth = do_auth
        self.do_verbose = do_verbose
        self.dir = Path(directory)
        server_port = server_port.split(':')
        self.server = server_port[0]
        self.port = int(server_port[1])

        if self.do_auth:
            self.password = getpass()

        self.commands = []
        self.set_commands()

    def set_commands(self):
        if self.do_auth:
            self.commands = [f'EHLO {self.login_from.replace("@", ".")}\n', 'auth login\n',
                             f'{base64.b64encode(self.login_from.encode("utf-8")).decode("utf-8")}\n',
                             f'{base64.b64encode(self.password.encode("utf-8")).decode("utf-8")}\n',
                             f'MAIL FROM: <{self.login_from}>\nRCPT TO: <{self.to}>\nDATA\n']
        else:
            self.commands = [f'EHLO {self.login_from.replace("@", ".")}\n',
                             f'MAIL FROM: <{self.login_from}>\nRCPT TO: <{self.to}>\nDATA\n']

    def create_mail(self):
        mail_creator = MailCreator()
        mail_creator.set_header(self.login_from, self.to, self.subject)
        files = self.get_images()
        for i, file in enumerate(files):
            if i == len(files) - 1:
                mail_creator.set_content(file, True)
            else:
                mail_creator.set_content(file, False)

        return mail_creator.get_letter()

    def get_images(self):
        return [File(Path(self.dir / filename)) for filename in os.listdir(self.dir) if
                filename.endswith('.jpg') or filename.endswith('.png') or filename.endswith('.jpeg')]

    def recv_msg(self, sock: socket):
        msg = sock.recv(1024).decode('utf-8')
        ans = Answer(msg)
        if ans.last_code > 499:
            raise Exception(ans.all_msg)

        if self.do_verbose:
            print(f'Server: {msg}')

    def send_msg(self, sock: socket, msg: str):
        if self.do_verbose:
            print(f'User: {msg}')
        sock.send(msg.encode())

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self.server, self.port))
            self.recv_msg(sock)
            if self.is_ssl:
                self.send_msg(sock, f'EHLO {self.login_from.replace("@", ".")}\n')
                self.recv_msg(sock)
                self.send_msg(sock, 'starttls\n')
                self.recv_msg(sock)
                sock = ssl.wrap_socket(sock)
            for command in self.commands:
                self.send_msg(sock, command)
                self.recv_msg(sock)
                if 'DATA' in command:
                    sock.send(self.create_mail().encode())
                    self.recv_msg(sock)

        except SMTPError as e:
            print(e)
        finally:
            sock.close()


class Answer:
    def __init__(self, msg: str):
        self._parse_msg(msg)

    def _parse_msg(self, msg: str):
        self.all_msg = msg
        msg_parts = msg.split('\n')[:-1]
        self.last_code = int(msg_parts[-1][0:4])
        self.last_msg = msg_parts[-1][5:]

    def __str__(self):
        return self.all_msg
