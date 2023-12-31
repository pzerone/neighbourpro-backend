import os
import logging
import logging.handlers

console_logger = logging.getLogger('console_logger')
multi_logger = logging.getLogger('multi_logger')

loggers = [console_logger, multi_logger]

for logger in loggers:
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
os.makedirs(logs_dir, exist_ok=True)
file_path = os.path.join(logs_dir, 'log_file.log')
file_handler = logging.handlers.RotatingFileHandler(file_path, maxBytes=10485760, backupCount=5)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
multi_logger.addHandler(file_handler)

def logit(message: str, level: int, to_file: bool = False) -> None:
    levels = (10, 20, 30, 40)
    if level not in levels:
        raise ValueError("invalid log level")
    if to_file:
        multi_logger.log(level, message)
    else:
        console_logger.log(level, message)


