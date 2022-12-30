# -*- coding: utf-8 -*-
# @Time    : 9/22/22 11:04 PM
# @FileName: Base.py
# @Software: PyCharm
# @Github    ：sudoskys
import os
import re
import uuid

import rtoml


def random_filename(filename):
    ext = os.path.splitext(filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename


def hash_file_name(filename):
    import hashlib
    m = hashlib.md5()
    m.update(bytes(filename, encoding="utf8"))
    return str(m.hexdigest()[:8])


def filter_str(name):
    """
    过滤非法字符
    :param name:
    :return: able use str
    """
    name = name.replace('"', '_')  # 消除目标对路径的干扰
    name = name.replace("'", '_')
    # remove = string.punctuation
    table = str.maketrans(r'~!#$%^&,{}\/？?', '______________', "")
    return name.translate(table)


class Dict(dict):
    __setattr__ = dict.__setitem__
    __getattr__ = dict.__getitem__


class Tool(object):

    def dictToObj(self, dictObj):
        if not isinstance(dictObj, dict):
            return dictObj
        d = Dict()
        for k, v in dictObj.items():
            d[k] = self.dictToObj(v)
        return d


class ReadConfig(object):
    def __init__(self, config=None):
        """
        read some further config!

        param paths: the file path
        """
        self.config = config

    def get(self):
        return self.config

    def parseFile(self, paths: str, toObj: bool = False):
        data = rtoml.load(open(paths, 'r'))
        self.config = Tool().dictToObj(data) if toObj else data
        return self.config
