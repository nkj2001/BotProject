import logging
import datetime
import os
current_file_path = __file__
dir_name = os.path.dirname(os.path.abspath(current_file_path))
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

def log_message(message):
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    file_name = f"{current_date}.txt"
    log = f"{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - {message}\n"
    with open(f"{dir_name}/log/{file_name}", "a", encoding="utf-8") as file:
        file.write(log)