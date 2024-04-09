import logging
import logging.handlers

console_logger = logging.getLogger("console_logger")

console_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(levelname)-10s%(message)s")
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_logger.addHandler(console_handler)


def msg_logger(message: str, level: int) -> None:
    """
    Levels:
    - 10: DEBUG
    - 20: INFO
    - 30: WARNING
    - 40: ERROR
    """
    levels = (10, 20, 30, 40)
    if level not in levels:
        raise ValueError("invalid log level")
    console_logger.log(level, message)
