# -*- coding: utf-8 -*-
# @Time    : 12/29/22 9:50 PM
# @FileName: Setting.py
# @Software: PyCharm
# @Github    ：sudoskys
import pathlib

from utils.Base import ReadConfig

global config


def get_app_config():
    global config
    obj = ReadConfig()
    config = obj.parseFile(str(pathlib.Path.cwd()) + "/Config/config.toml", toObj=False)
    return config
