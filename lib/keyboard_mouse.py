from ctypes import windll


def mouse_move(x, y):
    windll.user32.SetCursorPos(x, y)


def mouse_click(x, y):
    mouse_move(x, y)
    windll.user32.mouse_event(2, 0, 0, 0, 0)  # left down
    windll.user32.mouse_event(4, 0, 0, 0, 0)  # left up


def mouse_double_click(x, y):
    mouse_move(x, y)
    windll.user32.mouse_event(2, 0, 0, 0, 0)  # left down
    windll.user32.mouse_event(4, 0, 0, 0, 0)  # left up
    windll.user32.mouse_event(2, 0, 0, 0, 0)  # left down
    windll.user32.mouse_event(4, 0, 0, 0, 0)  # left up


def mouse_right_click(x, y):
    mouse_move(x, y)
    windll.user32.mouse_event(8, 0, 0, 0, 0)  # right down
    windll.user32.mouse_event(16, 0, 0, 0, 0)  # right up


def keyboard_press(key):
    windll.user32.keybd_event(key, 0, 0, 0)


def keyboard_release(key):
    windll.user32.keybd_event(key, 0, 2, 0)


def keyboard_press_and_release(key):
    keyboard_press(key)
    keyboard_release(key)


def keyboard_press_and_release_arrow(direction):
    arrow_keys = {"up": 0xC8, "down": 0xD0, "left": 0xCB, "right": 0xCD}
    key = arrow_keys.get(direction.lower())

    if key is not None:
        keyboard_press_and_release(key)


def mouse_middle_click():
    windll.user32.mouse_event(32, 0, 0, 0, 0)  # middle down
    windll.user32.mouse_event(64, 0, 0, 0, 0)  # middle up


def get_mouse_middle_is_pressed():
    return windll.user32.GetKeyState(0x04)


if __name__ == "__main__":
    print("this is a library")
    mouse_move(100, 100)
    mouse_right_click(100, 120)
