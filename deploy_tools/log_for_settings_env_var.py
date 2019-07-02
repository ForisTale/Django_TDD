import os
import datetime


def append_to_my_log_file():
    time_stamp = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    path = os.getcwd()
    path = path[:-12]
    with open(path+".my_log", "a") as log:
        log.write(time_stamp + " Settings.py has access to environment variables.\n")
