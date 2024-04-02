import json
from pathlib import Path
from enum import Enum


class AssetDir(Enum):
    CONFIG = 'config'
    SCRIPTS = 'scripts'


class ConfigFiles(Enum):
    DEFAULT = 'default.json'


def get_AssetDir_path(subpath: AssetDir) -> Path:
    return Path(__file__).parent.joinpath('asset', subpath.value)


def get_ConfigFile(filename=ConfigFiles.DEFAULT.value) -> Path:
    return get_AssetDir_path(AssetDir.CONFIG).joinpath(filename)


def save_ConfigFile(filename=ConfigFiles.DEFAULT.value, data: dict = None):
    if not data: return
    path = get_ConfigFile(filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, fp=f)


def get_ScriptDir():
    return get_AssetDir_path(AssetDir.SCRIPTS)


def get_ScriptFile(filename):
    return get_ScriptDir().joinpath(filename)


