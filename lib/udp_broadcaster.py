import socket
import time
import os

SERVER_INFO_FLAG = True


def new_boradcaster(_host, _port):
    global SERVER_INFO_FLAG

    interfaces = socket.getaddrinfo(
        host=socket.gethostname(), port=None, family=socket.AF_INET)
    allips = [ip[-1][0] for ip in interfaces]
    _message = f'{_host}'.encode("ascii")
    _max_attempts = 10
    _flag = True
    if SERVER_INFO_FLAG:
        print(f'{_message} sent at port {_port}.')
    SERVER_INFO_FLAG = False
    while _flag:
        for ip in allips:
            try:
                sock = socket.socket(
                    socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
                sock.setsockopt(socket.SOL_SOCKET,
                                socket.SO_EXCLUSIVEADDRUSE, 1)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.settimeout(0.2)
                sock.bind((ip, 0))
                sock.sendto(_message, ("<broadcast>", _port))
                sock.close()
            except OSError:
                print('error')
                _max_attempts -= 1
                if _max_attempts == 0:
                    print('max attempts reached')
                    os._exit(1)
                else:
                    continue

        time.sleep(2)


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def message_sender(_server, _port, _message):
    _server.sendto(_message, ("<broadcast>", _port))
    time.sleep(1)


def broadcast_ip_udp(_host, _port):
    global SERVER_INFO_FLAG

    server = socket.socket(
        socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # Enable port reuse so we will be able to run multiple clients and servers on single (host, port).
    # Do not use socket.SO_REUSEADDR except you using linux(kernel<3.9): goto
    # https://stackoverflow.com/questions/14388706/how-do-so-reuseaddr-and-so-reuseport-differ
    # for more information.
    # For linux hosts all sockets that want to share the same address and port combination,
    # must belong to processes that share the same effective user ID!
    # So, on linux(kernel>=3.9)
    # you have to run multiple servers and clients under one user to share the same (host, port).
    # Thanks to @stevenreddie
    server.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)

    # Enable broadcasting mode
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Set a timeout so the socket does not block
    # indefinitely when trying to receive data.
    server.settimeout(0.2)
    message = f'{_host}'.encode("ascii")

    if SERVER_INFO_FLAG:
        print(f'{message} sent at port 2525.')
    SERVER_INFO_FLAG = False

    while True:
        error_flag = False
        try:
            if error_flag:
                print("Connected")
            message_sender(server, _port, message)
        except OSError:
            error_flag = True
            print("Server disconnected, reconecting in 30 seconds")
            time.sleep(30)
            continue


if __name__ == '__main__':
    #broadcast_ip_udp()
    print("This is a module, not a script.")
