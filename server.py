#!/usr/bin/env python3
import os
import socket
import threading
import webbrowser
from datetime import datetime

from services.read_write import FileManipulation
import keyboard

from get_title_from_url import get_title_from_url

"""
this is a tcp server that receive a link and open it in a new tab (default browser)
"""

if not os.path.exists('./database'):
    os.makedirs('./database')

HOST_NAME = socket.gethostname()
HOST = socket.gethostbyname(HOST_NAME)
# PORT = int(input('The port you want to use: '))
PORT = 1007

FILE_MANIPULATION = FileManipulation()


def server(host, port):
    print(f'{host} is listening at port {port}')
    buffer_size = 1024
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    conn, address = server_socket.accept()
    print(f'accepted connection from {address}')
    data = conn.recv(buffer_size)
    command = data.decode()
    if command.startswith('https'):
        if command.__contains__("https://youtu.be/") or command.__contains__("youtube"):
            print("Server received url", command)
            webbrowser.open_new_tab(command)
            archive('youtube', command)
        else:
            print("Server received url", command)
            webbrowser.open_new_tab(command)
            archive('link', command)
    else:
        print("Server received command", command)
        keyboard.press_and_release(command)


def date_now():
    # dd/mm/YY H:M:S
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")


def archive(source, content):
    info_to_write = {'title': get_title_from_url(content), 'url': content, 'date': date_now()}
    FILE_MANIPULATION.write_to_disk(f'database/{source}_archive', 'json', info_to_write)


def main():
    my_server = threading.Thread(target=server, args=(HOST, PORT))
    my_server.start()
    my_server.join()


if __name__ == '__main__':
    while True:
        main()
