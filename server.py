#!/usr/bin/env python3
import os
import socket
from threading import Thread
import keyboard
import webbrowser
import winshell
import PySimpleGUI as sg
from datetime import datetime
from udp_broadcaster import broadcast_ip_udp
from services.read_write import FileManipulation
from services.create_windows_shortcut import startup_dir_location
from services.create_windows_shortcut import desktop_location
from services.create_windows_shortcut import CreateShortcut
from get_title_from_url import get_title_from_url
from turn_off_screen import turn_off_screen

"""
this is a tcp tcp_client that receive a link and open it in a new tab (default browser)
"""


def create_shortcut_to_startup():
    shortcut_name = 'OpenLinkServer.lnk'
    file_path = f'{desktop_location()}/Open_link_server'

    create_shortcut = CreateShortcut(startup_dir_location(), shortcut_name)
    create_shortcut.file_base_location = file_path
    create_shortcut.file_name = 'server.exe'
    create_shortcut.description = 'Open link server startup shortcut'
    create_shortcut.create_shortcut()


def create_archive_directory():
    # create directory if it didn't exist
    if not os.path.exists('./database'):
        os.makedirs('./database')


def tcp_client(host, port):
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
    print(f'Server received {link}')
    webbrowser.open_new_tab(link)
    if link.__contains__('https://youtu.be/') or link.__contains__('youtube'):
        archive('youtube', link)
    else:
        archive('link', link)


def bluetooth_handler(status):
    bluetooth_script_dir = r".\bluetooth_service"
    print(f'Server received {status}')
    if status.__contains__('on'):
        os.system(f'{bluetooth_script_dir}\connect.vbs')
    elif status.__contains__('off'):
        os.system(f'{bluetooth_script_dir}\disconnect.vbs')


def message_handler(message):
    if message.startswith('https'):
        link_handler(message)
    elif message.__contains__('bluetooth'):
        bluetooth_handler(message)
    elif message.__contains__('turn_off_screen'):
        turn_off_screen()
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

    tcp_server = Thread(target=tcp_client, args=(HOST, PORT))
    tcp_server.start()

    # udp_server.join()
    tcp_server.join()


if __name__ == '__main__':
    create_shortcut_to_startup()
    create_archive_directory()

    """ trying graphical interface problem with thread and graphic loop
        layout = [[sg.Text("192.168.11.104 is listening at port 1007")], [sg.Button("OK")]]

        # Create the window
        window = sg.Window("OpenLinkServer", layout)

        # Create an event loop
        while True:
            event, values = window.read()
            # End program if user closes window or
            # presses the OK button
            main()
            if event == "OK" or event == sg.WIN_CLOSED:
                break

        window.close()"""

    while True:
        main()


