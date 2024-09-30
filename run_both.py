import threading
import time

import receive_v2
import send


def main():
    send_thread = threading.Thread(target=send.main, daemon=True)
    receive_thread = threading.Thread(target=receive_v2.main, daemon=True)

    receive_thread.start()
    send_thread.start()


if __name__ == "__main__":
    main()
    # receive.main()
