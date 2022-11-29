import time
import os
from pathlib import Path

from colorama import Fore, init


def follow(filename: Path, sleep: float = None, tail=False) -> str:
    if sleep is None:
        sleep = 1.0

    with filename.open(mode='r') as f:
        if tail:
            f.seek(0, os.SEEK_END)

        while True:
            line = f.readline()

            if not line:
                time.sleep(sleep)
                continue

            yield line

def convert(line: str) -> dict:
    raw = line.split()

    frame = dict(
        zip(('number', 'timestamp', 'direction', 'id', 'length'), raw))

    len = int(frame.get('length', '0'))

    if len > 0:
        frame['data'] = raw[5:(5+len)]

    f = dict(zip(('checksum', 'type', 'error'), raw[5+len:]), strict=True)

    frame = {**frame, **f}

    frame['raw'] = line

    return frame


def trace(msg: dict) -> str:
    time = int(msg['timestamp'])/1000
    data = " ".join(msg.get('data', []))

    return f"{time:>10.0f} {msg['id']:>4s} {msg['length']:>3s}  {data:<26s} {msg.get('error', '')}"


def _print(color: str, line: str):

    print(f"{color}{line}", end='')


def main(args):
    init(autoreset=True)

    verbose = False

    ltrc = Path(args.tracefile).with_suffix('.ltrc')

    if not ltrc.is_file():
        ltrc = Path(os.getenv('userprofile'), 'Documents').joinpath(
            args.tracefile).with_suffix('.ltrc')

    print(ltrc)

    if args.filter is not None:
        filter = [f"{int(i, base=0):02X}" for i in args.filter]
    else:
        filter = list()

    for line in follow(ltrc, sleep=args.sleep, tail=args.tail):
        if line.startswith(';'):
            continue

        frame = convert(line)

        if args.error:
            if frame.get('error', None) is not None:
                _print(Fore.RED, line)
                continue

        if args.diag:
            if frame.get('id', None) == '3C':
                _print(Fore.YELLOW, line)
                continue

            if frame.get('id', None) == '3D':
                _print(Fore.GREEN, line)
                continue

        if filter:
            if frame.get('id', '') in filter:
                _print(Fore.CYAN, line)
                continue

        if args.verbose:
            _print(Fore.RESET, line)


def arguments():
    import argparse

    p = argparse.ArgumentParser(
        description='load *.ltrc readonly continually and print message into stdout')
    p.add_argument('tracefile', help='peak-can *.ltrc')
    p.add_argument(
        '-f', '--filter', help="specify multiple id's which are shown in CYAN ",
        nargs='*', default=None, type=str
    )
    p.add_argument(
        '-e', '--error', help='print all messages in RED where an error occured', action='store_true')
    p.add_argument(
        '-d', '--diag', help='show diagnostic requests 0x3C in YELLOW and responses 0x3D green', action='store_true')
    p.add_argument(
        '-v', '--verbose',
        help='display all messages other messages in WHITE', action='store_true'
    )
    p.add_argument(
        '-s', '--sleep', help='polling time in seconds for tailing the ltrc file', type=float, default=0.1
    )
    p.add_argument(
        '-t', '--tail', help='display only new added lines in file', action='store_true')

    return p.parse_args()


if __name__ == '__main__':
    args = arguments()

    try:
        main(args)
    except KeyboardInterrupt:
        print('done')
