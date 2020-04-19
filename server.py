#!/usr/bin/env python3
import os
import socket
import keyboard
import webbrowser

from threading import Thread
from datetime import datetime
from udp_broadcaster import broadcast_ip_udp
from services.read_write import FileManipulation
from get_title_from_url import get_title_from_url

"""
this is a tcp server that receive a link and open it in a new tab (default browser)
"""


def create_archive_directory():
    # create directory if it didn't exist
    if not os.path.exists('./database'):
        os.makedirs('./database')


def server(host, port):
    print(f'{host} is listening at port {port}')
    buffer_size = 1024
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    conn, address = server_socket.accept()
    print(f'accepted connection from {address}')
    data = conn.recv(buffer_size)
    message_handler(data.decode())


def command_handler(command):
    print(f'Server received command {command}')
    keyboard.press_and_release(command)


def link_handler(link):
    print("Server received url", link)
    webbrowser.open_new_tab(link)
    if link.__contains__("https://youtu.be/") or link.__contains__("youtube"):
        archive('youtube', link)
    else:
        archive('link', link)


def message_handler(message):
    if message.startswith('https'):
        link_handler(message)
    else:
        command_handler(message)


def date_now():
    # dd/mm/YY H:M:S
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")


def archive(source, content):
    FILE_MANIPULATION = FileManipulation()
    info_to_write = {'title': get_title_from_url(content), 'url': content, 'date': date_now()}
    FILE_MANIPULATION.write_to_disk(f'database/{source}_archive', 'json', info_to_write)


def main():
    # get the ip of the host from the hostname
    HOST = socket.gethostbyname(socket.gethostname())
    # port number
    PORT = 1007

    udp_server = Thread(target=broadcast_ip_udp)
    udp_server.start()

    tcp_server = Thread(target=server, args=(HOST, PORT))
    tcp_server.start()

    udp_server.join()
    tcp_server.join()


if __name__ == '__main__':
    create_archive_directory()
    while True:
        main()
