import json
import os
from pathlib import Path
from enum import Enum
from typing import Union


class AssetDir(Enum):
    CONFIG = 'config'
    SCRIPTS = 'scripts'


class ConfigFiles(Enum):
    DEFAULT = 'default.json'


class ScriptType(Enum):
    pre_script = 'pre_script'
    post_script = 'post_script'
    foreach_pre_script = 'foreach_pre_script'
    foreach_post_script = 'foreach_post_script'


def get_AssetDir_path(subpath: AssetDir) -> Path:
    return Path(__file__).parent.joinpath('asset', subpath.value)


def get_ConfigDir() -> Path:
    return get_AssetDir_path(AssetDir.CONFIG)


def get_ConfigFile(filename=ConfigFiles.DEFAULT.value) -> Path:
    return get_AssetDir_path(AssetDir.CONFIG).joinpath(filename)


def save_ConfigFile(filename=ConfigFiles.DEFAULT.value, data: dict = None):
    if not data: return
    path = get_ConfigFile(filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, fp=f)


def get_ScriptDir() -> Path:
    return get_AssetDir_path(AssetDir.SCRIPTS)


def get_ScriptFile(filename) -> Union[Path, None]:
    # walk through all files in the script directory
    for root, dirs, files in os.walk(get_ScriptDir()):
        for file in files:
            if file == filename:
                return Path(root).joinpath(file)
    return None
