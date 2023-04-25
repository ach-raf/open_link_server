#!/usr/bin/env python3
import os
import socket
from threading import Thread
import keyboard
from pyKey import pressKey, releaseKey
import webbrowser
import winshell
from datetime import datetime
from udp_broadcaster import broadcast_ip_udp, new_boradcaster
from services.file_handler.file_handler import FileManipulation
from services.create_windows_shortcut import startup_dir_location
from services.create_windows_shortcut import desktop_location
from services.create_windows_shortcut import CreateShortcut
from get_title_from_url import get_title_from_url
from turn_off_screen import turn_off_screen
from time import sleep

import lib.keyboard_mouse as keyboard_mouse

"""
this is a tcp tcp_client that receive a link and open it in a new tab (default browser)
"""


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


# ==============================================================================
CURRENT_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
FILE_MANIPULATION = FileManipulation(CURRENT_DIR_PATH)
# get the ip of the host from the hostname
HOST = get_ip_address()
# port number
PORT = 1007
UDP_PORT = 2525
counter_16_9 = 0
# ==============================================================================


def get_date(date_format):
    match date_format:
        case 'date_now':
            # dd/mm/YY H:M:S
            return datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        case 'today':
            # dd/mm/YY
            return datetime.now().strftime("%d-%m-%Y")
        case 'time_now':
            # H:M
            return datetime.now().strftime("%H:%M")


def press_and_release(_key):
    """
    this function uses the library pyKey that can handle the numpad strokes.
    used only to stretch 4:6 video to 16:9
    showKeys() to get the input code
    pressKey() will press a key and holds it until explicitly called the releaseKey function.
    releaseKey() will release a key that was pressed by pressKey function.
    :return:
    """

    pressKey(_key)
    releaseKey(_key)


def archive(source, content):
    archive_location = os.path.join('database', f'{source}_archive.json')
    info_to_write = {'title': get_title_from_url(
        content), 'url': content, 'date': get_date('date_now')}
    FILE_MANIPULATION.write_to_disk(archive_location, info_to_write)


def log_file(_info_to_write):
    log_location = os.path.join(
        'database', 'log_files', f'log - {get_date("today")}.txt')
    content = f'{_info_to_write} at {get_date("time_now")}\n'
    FILE_MANIPULATION.write_to_disk(log_location, content)


def commands_print(command):
    commands_dict = {'volume down': 'volume down', 'volume up': 'volume up', 'left arrow': '-10 seconds',
                     'right arrow': '+10 seconds', 'alt+left arrow': '-20 seconds', 'alt+right arrow': '+20 seconds',
                     'space': 'Play/Pause', 's': 'subtitle_button (s)', 'd': 'subtitle_search (d)',
                     'a': 'audio_button (a)', ';': 'stop_button', 'page down': 'next_chapter_button',
                     'page up': 'previous_chapter_button', 'ctrl+page down': 'skip_forward_button',
                     'ctrl+page up': 'skip_back_button',
                     'turn_off_screen': 'turn_off_screen', 'skip_anime_intro': 'skip_anime_intro',
                     '16_9': 'stretch_to_16_9', 'f1': 'F1', 'f2': 'F2'}
    try:
        print(f'Server received command {commands_dict[command]}')
        log_file(f'Server received command {commands_dict[command]}')
    except KeyError:
        print(f'Server received command {command}')
        log_file(f'Server received command {command}')


def create_shortcut_to_startup():
    shortcut_name = 'OpenLinkServer.lnk'
    file_path = f'{desktop_location()}/Open_link_server'

    create_shortcut = CreateShortcut(startup_dir_location(), shortcut_name)
    create_shortcut.file_base_location = file_path
    create_shortcut.file_name = 'server.exe'
    create_shortcut.description = 'Open link server startup shortcut'
    create_shortcut.create_shortcut()


def skip_anime_intro():
    """
    anime intro is 1m30s generally
    alt+right arrow = +20s
    //right arrow = +10s
    """
    keyboard.press_and_release("space")
    for i in range(4):
        keyboard.press_and_release("alt+right arrow")
        sleep(0.2)
    keyboard.press_and_release("right arrow")
    sleep(0.1)
    keyboard.press_and_release("space")


def command_handler(command):
    commands_print(command)
    match command:
        case 'skip_anime_intro':
            skip_anime_intro()
        case '16_9':
            global counter_16_9

            match counter_16_9:
                case 0:
                    print("stretching wide")
                    for i in range(14):
                        # wide stretch in mpc
                        press_and_release('NUM6')
                    """counter_16_9 = 1
                case 1:
                    print("movie look, top and bottom bars")
                    for i in range(15):
                        # movie look; add top and bottom bars,
                        press_and_release('NUM2')
                    counter_16_9 = 2
                case 2:
                    print("return to normal")
                    # return to normal
                    for i in range(15):
                        press_and_release('NUM4')
                        press_and_release('NUM8')
                    counter_16_9 = 0"""
        case _:
            if command != "":
                keyboard.press_and_release(command)


def link_handler(link):
    print(f'Server received {link}')
    log_file(f'Server received {link}')
    webbrowser.open_new_tab(link)
    if link.__contains__('https://youtu.be/') or link.__contains__('youtube'):
        archive('youtube', link)
    else:
        archive('link', link)


def bluetooth_handler(status):
    bluetooth_script_dir = os.path.join(CURRENT_DIR_PATH, 'bluetooth_service')
    print(f'Server received {status}')
    log_file(f'Server received {status}')
    if status.__contains__('on'):
        os.system(os.path.join(bluetooth_script_dir, 'connect.vbs'))
    elif status.__contains__('off'):
        os.system(os.path.join(bluetooth_script_dir, 'disconnect.vbs'))


def message_handler(message):
    if message.startswith('https') or '.com' in message:
        link_handler(message)
    elif message.__contains__('bluetooth'):
        bluetooth_handler(message)
    elif message.__contains__('turn_off_screen'):
        turn_off_screen()
    else:
        command_handler(message)


def tcp_client(host, port):
    buffer_size = 1024
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    conn, address = server_socket.accept()
    # print(f'accepted connection from {address}')
    data = conn.recv(buffer_size)
    message_handler(data.decode())


def server():

    udp_server = Thread(target=new_boradcaster, args=(HOST, UDP_PORT))
    udp_server.start()

    tcp_server = Thread(target=tcp_client, args=(HOST, PORT))
    tcp_server.start()

    # udp_server.join()
    tcp_server.join()


def main():

    # create_shortcut_to_startup()
    print(f'{HOST} is listening at port {PORT}')
    while True:
        server()


if __name__ == '__main__':
    main()
