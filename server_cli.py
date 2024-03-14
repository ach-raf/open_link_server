#!/usr/bin/env python3
import os
import socket
from threading import Thread
import keyboard
from pyKey import pressKey, releaseKey
import webbrowser
from datetime import datetime
from lib.udp_broadcaster import broadcast_ip_udp, new_boradcaster
from lib.turn_off_screen import turn_off_screen
from time import sleep


"""
this is a tcp tcp_client that receive a link and open it in a new tab (default browser)
"""


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


# ==============================================================================
CURRENT_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
# get the ip of the host from the hostname
HOST = get_ip_address()
# port number
PORT = 1007
UDP_PORT = 2525
# ==============================================================================


def get_date(date_format):
    match date_format:
        case "date_now":
            # dd/mm/YY H:M:S
            return datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        case "today":
            # dd/mm/YY
            return datetime.now().strftime("%d-%m-%Y")
        case "time_now":
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


def commands_print(command):
    commands_dict = {
        "volume down": "volume down",
        "volume up": "volume up",
        "alt+m": "mute volume",
        "left arrow": "-10 seconds",
        "right arrow": "+10 seconds",
        "alt+left arrow": "-20 seconds",
        "alt+right arrow": "+20 seconds",
        "space": "Play/Pause",
        "s": "subtitle_button (s)",
        "d": "subtitle_search (d)",
        "a": "audio_button (a)",
        ";": "stop_button",
        "page down": "next_chapter_button",
        "page up": "previous_chapter_button",
        "ctrl+page down": "skip_forward_button",
        "ctrl+page up": "skip_back_button",
        "turn_off_screen": "turn_off_screen",
        "skip_anime_intro": "skip_anime_intro",
        "16_9": "stretch_to_16_9",
        "f1": "F1",
        "f2": "F2",
        "esc": "ESC",
        "history": "h",
        "enter": "enter",
    }
    try:
        print(f"Server received command {commands_dict[command]}")
    except KeyError:
        print(f"Server received command {command}")


def skip_anime_intro():
    keyboard.press_and_release("shift+r")


def command_handler(command):
    commands_print(command)
    match command:
        case "skip_anime_intro":
            skip_anime_intro()
        case "16_9":
            keyboard.press_and_release("shift+m")
        case "left arrow":
            keyboard.press_and_release("shift+p")
        case "right arrow":
            keyboard.press_and_release("p")
        case "alt+left arrow":
            keyboard.press_and_release("ctrl+p")
        case "alt+right arrow":
            keyboard.press_and_release("ctrl+shift+p")
        case "page down":
            keyboard.press_and_release("i")
        case "page up":
            keyboard.press_and_release("u")
        case "ctrl+page down":
            keyboard.press_and_release("ctrl+shift+i")
        case "ctrl+page up":
            keyboard.press_and_release("ctrl+u")
        case "history":
            keyboard.press_and_release("h")
        case _:
            keyboard.press_and_release(command)


def link_handler(link):
    print(f"Server received {link}")
    webbrowser.open_new_tab(link)


def message_handler(message):
    if message.startswith("https") or ".com" in message:
        link_handler(message)
    elif message.__contains__("turn_off_screen"):
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
    print(f"{HOST} is listening at port {PORT}")
    while True:
        server()


if __name__ == "__main__":
    main()
