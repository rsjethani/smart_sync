#!/usr/bin/python3

import argparse
import logging
import subprocess
import threading
import time

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


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


class SyncFSThread(threading.Thread):
    def __init__(self, cmd_line, wait=3):
        super().__init__(daemon=True)
        self._cmd_line = cmd_line
        self.time_to_wait = wait
        self.last_change_time = 0
        self._fs_changed_event = threading.Event()
        self._stop_thread_event = threading.Event()

    def stop(self):
        self._stop_thread_event.set()

    def fs_has_changed(self):
        self._fs_changed_event.set()
        self.last_change_time = time.time()

    def run(self):
        while not self._stop_thread_event.is_set():
            time_elapsed = time.time() - self.last_change_time
            if self._fs_changed_event.is_set() and time_elapsed > self.time_to_wait:
                do_rsync(self._cmd_line)
                self._fs_changed_event.clear()
            time.sleep(2)
        # Before exiting check for any left over events and sync them
        if self._fs_changed_event.is_set():
            logging.info("syncing any remaining file system changes")
            do_rsync(self._cmd_line)


class AllEventHandler(PatternMatchingEventHandler):
    def __init__(self, thread_to_notify):
        super().__init__()
        self._thread = thread_to_notify

    def on_any_event(self, event):
        logging.info(event)
        # print("observer: ", event)
        self._thread.fs_has_changed()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("src", help="source file or directory to watch")
    parser.add_argument("dest", help="destination file or directory to "
                                     "synchronize")
    parser.add_argument("-d", "--delete", action="store_true",
                        help="delete extraneous files which only exist "
                             "at dest")
    parser.add_argument("-e", "--exclude", nargs="+",
                        help="list of file/directory names to exclude."
                             " You can also give wildcard patterns.")
    parser.add_argument("-f", "--exclude-from",
                        help="file from which to read exclude names and "
                             "patterns.")

    return parser.parse_args()


def main():
    logging.basicConfig(format="%(asctime)s:%(levelname)s: %(message)s", level=logging.INFO)
    args = parse_args()
    cmd_line = ["rsync", "-e", "ssh", "-ruvz"]
    if args.delete:
        cmd_line.append("--delete")
    if args.exclude_from:
        cmd_line.extend(["--exclude-from", args.exclude_from])
    for name in args.exclude:
        cmd_line.extend(["--exclude", name])
    cmd_line.extend([args.src, args.dest])


    observer_thread = Observer()
    sync_fs_thread = SyncFSThread(cmd_line)
    event_handler = AllEventHandler(sync_fs_thread)
    observer_thread.schedule(event_handler, args.src, recursive=True)

    logging.info("starting file system observer thread")
    observer_thread.start()
    logging.info("starting file system syncing thread")
    sync_fs_thread.start()

    try:
        while True:
            input()
    except (KeyboardInterrupt, EOFError):
        logging.info("terminating worker threads please wait")
        observer_thread.stop()
        sync_fs_thread.stop()

    observer_thread.join()
    sync_fs_thread.join()
    logging.info("exiting")


if __name__ == "__main__":
    main()
