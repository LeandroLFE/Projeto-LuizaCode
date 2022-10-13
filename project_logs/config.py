from utils.blender_bcolors import bcolors


def config(dados):
    return {
        "version": 1,
        "formatters": {
            "console": {
                "class": "logging.Formatter",
                "format": f"""{bcolors.WARNING}%(threadName)s %(processName)s %(asctime)s {bcolors.FAIL}{bcolors.BOLD
            }%(levelname)s{bcolors.WARNING} %(name)s{bcolors.ENDC}\n%(message)s\n""",
            },
            "file": {
                "class": "logging.Formatter",
                "format": "%(threadName)s %(processName)s %(asctime)s %(levelname)s %(name)s\n%(message)s\n",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "console",
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": f"{dados['filename']}.log",
                "mode": "a",
                "formatter": "file",
                "level": "INFO",
                "encoding": "UTF-8",
            },
        },
        "loggers": {
            dados["filename"]: {
                "handlers": ["file"],
            },
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["console"],
        },
    }
