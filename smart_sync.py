#!/usr/bin/env python3

import argparse
import logging
import subprocess
import threading
import time

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


def parse_args():

    def positive_integer(val):
        val = int(val)
        if val < 0:
            msg = "'{}' is not a positive integer".format(val)
            raise argparse.ArgumentTypeError(msg)
        return val

    parser = argparse.ArgumentParser()
    parser.add_argument("src", help="Source file or directory to watch")
    parser.add_argument("dest", help="Destination file or directory to "
                                     "synchronize")
    parser.add_argument("-d", "--delete", action="store_true",
                        help="Delete extraneous files which only exist "
                             "at dest")
    parser.add_argument("-e", "--exclude", nargs="+",
                        help="List of file/directory names to exclude."
                             " You can also give wildcard patterns.")
    parser.add_argument("-f", "--exclude-from",
                        help="File from which to read exclude names and "
                             "patterns.")
    parser.add_argument("-l", "--log-level", choices={"INFO", "DEBUG"},
                        default="INFO",
                        help="Set logging level. Default: INFO")
    parser.add_argument("-w", "--wait", type=positive_integer, default=3,
                        help="No. of seconds to wait after last event "
                             "before starting syncing process.")

    return parser.parse_args()


def build_rsync_command_line(args):
    """Build rsync command from command line arguments"""
    cmd_line = ["rsync", "-e", "ssh", "-ruvz"]
    if args.delete:
        cmd_line.append("--delete")
    if args.exclude_from:
        cmd_line.extend(["--exclude-from", args.exclude_from])
    if args.exclude:
        for name in args.exclude:
            cmd_line.extend(["--exclude", name])
    cmd_line.extend([args.src, args.dest])
    return cmd_line


def do_rsync(cmd_line):
    logging.debug("executing external command: {}".format(" ".join(cmd_line)))
    try:
        logging.info("syncing file system changes")
        out = subprocess.check_output(cmd_line, stderr=subprocess.STDOUT)
        logging.info("sync complete")
        logging.debug("external command output: {}".format(out))
    except subprocess.CalledProcessError as e:
        logging.error(e)
        logging.error("failing command says: {}".format(e.output))
        logging.warning("file system changes not synced")


class AllEventHandler(PatternMatchingEventHandler):
    def __init__(self, event):
        super().__init__()
        self.fs_event = event
        self.last_event_time = 0

    def on_any_event(self, event):
        self.last_event_time = time.time()
        self.fs_event.set()
        logging.info(event)


def main():
    args = parse_args()

    time_to_wait = args.wait
    cmd_line = build_rsync_command_line(args)
    logging.basicConfig(format="%(asctime)s:%(levelname)s: %(message)s",
                        level=args.log_level)

    logging.info("performing initial sync, please wait")
    do_rsync(cmd_line)

    fs_change_event = threading.Event()
    handler = AllEventHandler(fs_change_event)
    observer_thread = Observer()
    observer_thread.schedule(handler, args.src, recursive=True)
    logging.info("starting file system observer thread")
    observer_thread.start()

    logging.info("now watching path: {} for changes".format(args.src))
    try:
        while True:
            if fs_change_event.is_set():
                time_since_last_event = time.time() - handler.last_event_time
                if time_since_last_event > time_to_wait:
                    do_rsync(cmd_line)
                    fs_change_event.clear()
            time.sleep(2)
    except (KeyboardInterrupt, EOFError):
        logging.info("terminating observer threads please wait")
        observer_thread.stop()
        # Before exiting check for any left over events and sync them
        if fs_change_event.is_set():
            logging.info("syncing remaining file system changes")
            do_rsync(cmd_line)

    observer_thread.join()
    logging.info("exiting")


if __name__ == "__main__":
    main()
