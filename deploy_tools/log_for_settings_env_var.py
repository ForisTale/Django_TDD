import os
import datetime


def append_to_my_log_file(has_access, setting_message=""):
    time_stamp = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    path = os.getcwd()
    path = path[:-12]
    if has_access:
        message = time_stamp + " Settings.py has access to environment variables.\n"
    else:
        message = time_stamp + " Settings.py don't have access to environment variables.\n"
    with open(path+".my_log", "a") as log:
        log.write(message + setting_message + "\n")
