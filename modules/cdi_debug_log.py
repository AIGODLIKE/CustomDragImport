class DebugLevel():
    NONE = 0
    ERROR = 1
    WARNING = 2
    INFO = 3
    DEBUG = 4


class DebugColor():
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[0;33m'
    LIGHT_BLUE = '\033[0;36m'
    NONE = '\033[0m'


class DebugLog():
    header = '[CDI-%s]'
    level = 4

    @classmethod
    def set_header(cls, header):
        cls.header = header

    @classmethod
    def set_debug_level(cls, level):
        cls.level = level

    @staticmethod
    def info(*args):
        if DebugLog.level < 2:
            return
        print(DebugColor.GREEN, DebugLog.header % 'info', end=' ')
        print(DebugColor.NONE, *args)

    @staticmethod
    def error(*args):
        if DebugLog.level < 1:
            return
        print(DebugColor.RED, DebugLog.header % 'error', end=' ')
        print(DebugColor.NONE, *args)

    @staticmethod
    def warning(*args):
        if DebugLog.level < 1:
            return
        print(DebugColor.YELLOW, DebugLog.header % 'warning', end=' ')
        print(DebugColor.NONE, *args)

    @staticmethod
    def debug(*args):
        if DebugLog.level < 3:
            return
        print(DebugColor.LIGHT_BLUE, DebugLog.header % 'debug', end=' ')
        print(DebugColor.NONE, *args)
