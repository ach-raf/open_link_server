#!/usr/bin/env python3
import os
import socket
from threading import Thread
import keyboard
import webbrowser
import winshell
#import PySimpleGUI as sg
from datetime import datetime
from udp_broadcaster import broadcast_ip_udp
from services.read_write import FileManipulation
from services.create_windows_shortcut import startup_dir_location
from services.create_windows_shortcut import desktop_location
from services.create_windows_shortcut import CreateShortcut
from get_title_from_url import get_title_from_url
from turn_off_screen import turn_off_screen
from time import sleep

import wx.adv
import wx

from pyKey import pressKey, releaseKey, sendSequence

server_info_flag = True


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
        os.makedirs('./database/log_files')


def tcp_client(host, port):
    global server_info_flag
    if server_info_flag:
        print(f'{host} is listening at port {port}')
        log_file(f'{host} is listening at port {port}')
    buffer_size = 1024
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    conn, address = server_socket.accept()
    if server_info_flag:
        print(f'accepted connection from {address}')
        log_file(f'accepted connection from {address}')

    data = conn.recv(buffer_size)
    message_handler(data.decode())
    server_info_flag = False


def skip_anime_intro():
    """
    anime intro is 1m30s generally
    alt+right arrow = +20s
    //right arrow = +10s
    because mpc skips too much due to fast virtual clicks after some trial and error, found these options works
    """
    # go back 10 seconds because mpc uses segments, so it won't skip too forward.
    keyboard.press_and_release("left arrow")
    for i in range(4):
        keyboard.press_and_release("alt+right arrow")
        sleep(0.35)
    keyboard.press_and_release("right arrow")


def command_handler(command):
    commands_print(command)
    if command == 'skip_anime_intro':
        skip_anime_intro()
    elif command == '16_9':
        for i in range(15):
            press_and_release('NUM6')
    else:
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
    bluetooth_script_dir = r".\bluetooth_service"
    print(f'Server received {status}')
    log_file(f'Server received {status}')
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


def date_today():
    # dd/mm/YY
    return datetime.now().strftime("%d-%m-%Y")


def time_now():
    # H:M
    return datetime.now().strftime("%H:%M")


def commands_print(command):
    commands_dict = {'volume down': 'volume down', 'volume up': 'volume up', 'left arrow': '-10 seconds',
                     'right arrow': '+10 seconds', 'alt+left arrow': '-20 seconds', 'alt+right arrow': '+20 seconds',
                     'space': 'Play/Pause', 's': 'subtitle_button (s)', 'd': 'subtitle_search (d)',
                     'a': 'audio_button (a)', ';': 'stop_button', 'page down': 'next_chapter_button',
                     'page up': 'previous_chapter_button', 'ctrl+page down': 'skip_forward_button',
                     'ctrl+page up': 'skip_back_button',
                     'turn_off_screen': 'turn_off_screen', 'skip_anime_intro': 'skip_anime_intro',
                     '16_9': 'stretch_to_16_9'}
    try:
        print(f'Server received command {commands_dict[command]}')
        log_file(f'Server received command {commands_dict[command]}')
    except KeyError:
        print(f'Server received command {command}')
        log_file(f'Server received command {command}')


def archive(source, content):
    FILE_MANIPULATION = FileManipulation()
    info_to_write = {'title': get_title_from_url(
        content), 'url': content, 'date': date_now()}
    FILE_MANIPULATION.write_to_disk(
        f'database/{source}_archive', 'json', info_to_write)


def log_file(_info_to_write):
    FILE_MANIPULATION = FileManipulation()
    FILE_MANIPULATION.write_to_disk(f'database/log_files/log - {date_today()}', 'txt',
                                    f'{_info_to_write} at {time_now()}\n')


TRAY_TOOLTIP = 'Open Link server'
TRAY_ICON = 'icon.png'
# Define notification event for thread completion
EVT_RESULT_ID = wx.NewId()


def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.Append(item)
    return item


class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame):
        self.frame = frame
        super(TaskBarIcon, self).__init__()
        self.set_icon(TRAY_ICON)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)
        self.status = 'None'
        self.bluetooth_status = False
        # And indicate we don't have a worker thread yet
        self.worker = None

    def CreatePopupMenu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Start Server', self.start_server)
        create_menu_item(menu, 'Bluetooth on/off', self.bluetooth_on_off)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def set_icon(self, path):
        icon = wx.Icon(path)
        self.SetIcon(icon, TRAY_TOOLTIP)

    def on_left_down(self, event):
        self.start_server(event)

    def start_server(self, event):
        """Start Computation."""
        # Trigger the worker thread unless it's already busy

        if self.worker is None:
            self.status = 'Starting computation'
            self.worker = WorkerThread(self)
        else:
            self.status = 'Server Already started'
            print('Server Already started')
            log_file('Server Already started')

    def bluetooth_on_off(self, event):
        if not self.bluetooth_status:
            self.bluetooth_status = True
            bluetooth_handler('on')
        else:
            self.bluetooth_status = False
            bluetooth_handler('off')

    def on_exit(self, event):
        if self.worker is not None:
            self.worker.abort()
        wx.CallAfter(self.Destroy)
        self.frame.Close()
        os._exit(1)


def evt_result(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)


class ResultEvent(wx.PyEvent):
    """Simple event to carry server result data."""

    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data


class WorkerThread(Thread):
    """Worker Thread Class."""

    def __init__(self, notify_window):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self._notify_window = notify_window
        self._want_abort = 0
        self._server_running = 1
        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()

    def run(self):
        """Run Worker Thread."""
        # This is the code executing in the new thread. Simulation of
        # a long process (well, 10s here) as a simple loop - you will
        # need to structure your processing so that you periodically
        # peek at the abort variable
        while self._server_running == 1:
            server()
            if self._want_abort:
                # Use a result of None to acknowledge the abort (of
                # course you can use whatever you'd like or even
                # a separate event type)
                wx.PostEvent(self._notify_window, ResultEvent(None))
                return
        # Here's where the result would be returned (this is an
        # example fixed result of the number 10, but it could be
        # any Python object)
        wx.PostEvent(self._notify_window, ResultEvent(10))

    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
        self._server_running = 0
        self._want_abort = 1


class App(wx.App):
    def OnInit(self):
        frame = wx.Frame(None)
        self.SetTopWindow(frame)
        TaskBarIcon(frame)
        return True


def server():
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


def main():
    app = App(False)
    app.MainLoop()


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

    main()
