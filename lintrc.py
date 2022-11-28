import time
import os
from pathlib import Path

from colorama import Fore, init


def follow(filename: Path, s: float = None) -> str:
    if s is None:
        s = 1.0

    with filename.open(mode='r') as f:
        while True:
            line = f.readline()

            if not line:
                time.sleep(s)
                continue

            yield line


trc = [
    " 1)           756186   Sub   02  2  -- --                    00  EH  SR/TO ",
    " 2)           781185   Sub   3C  8  -- -- -- -- -- -- -- --  00  EH  SR/TO ",
    " 3)           806186   Pub   05  2  00 00                    7A  EH   ",
    " 4)           831184   SubAL 02  0                           00  EH  SR/TO ",
    " 5)           856183   Sub   3D  8  C1 38 FE FF 3F F0 3E 6D  FC  EH  CK ",
    " 6)           881183   Pub   05  2  00 00                    7A  EH   ",
    " 7)           906182   Sub   02  2  FC 7F                    41  EH  ",
    " 8)           931181   Sub   01  8  C1 38 FE FF 3F F0 E6 6A  C3  EH "
]


def convert(line: str) -> dict:
    raw = line.split()

    frame = {'raw': line}

    frame |= dict(
        zip(('number', 'timestamp', 'direction', 'id', 'length'), raw))

    len = int(frame.get('length', '0'))

    if len > 0:
        frame['data'] = raw[5:(5+len)]

    frame |= dict(zip(('checksum', 'type', 'error'), raw[5+len:]), strict=True)

    return frame


def trace(msg: dict) -> str:
    time = int(msg['timestamp'])/1000
    data = " ".join(msg.get('data', []))

    return f"{time:>10.0f} {msg['id']:>4s} {msg['length']:>3s}  {data:<26s} {msg.get('error', '')}"


def _print(color: str, line: str):

    print(f"{color}{line}", end='')


def main():
    init(autoreset=True)

    filter = {0x23}
    verbose = False

    ltrc = Path(r"C:\Users\christoph.doerrer\Documents\Untitled.ltrc")

    if not ltrc.is_file():
        ltrc = Path('Untitled.ltrc')

    for line in follow(ltrc, s=0.1):
        if line.startswith(';'):
            continue

        frame = convert(line)

        if frame.get('error', None) is not None:
            _print(Fore.RED, line)
            continue

        if frame.get('id', '') == '3C':
            _print(Fore.YELLOW, line)
            continue

        if frame.get('id', '') == '3D':
            _print(Fore.GREEN, line)
            continue

        if frame.get('id', '') in [f"{i:02X}" for i in filter]:
            _print(Fore.CYAN, line)
            continue

        if verbose is True:
            _print(Fore.RESET, line)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('done')
