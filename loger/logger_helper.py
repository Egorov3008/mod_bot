import logging
import json
import logging.config


class LevelFilter(logging.Filter):
    def __init__(self, level):
        super().__init__()
        self.level = level

    def filter(self, record):
        return record.levelno == self.level


class LevelFileHandler(logging.FileHandler):
    def __init__(self, file_name, level=logging.NOTSET, filter=None, *args, **kwargs):
        super().__init__(file_name, *args, **kwargs)
        self.file_name = file_name
        self.setLevel(level)
        if filter is not None:
            self.addFilter(filter)

    def emit(self, record: logging.LogRecord):
        message = self.format(record)

        with open(self.file_name, self.mode) as f:
            f.write(message + '\n')


with open("loger/logger_helper.json", 'r') as file:
    dict_config = json.load(file)


def get_logger(name):
    logging.config.dictConfig(dict_config)
    return logging.getLogger(name)



