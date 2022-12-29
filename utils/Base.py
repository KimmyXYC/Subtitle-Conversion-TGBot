# -*- coding: utf-8 -*-
# @Time    : 9/22/22 11:04 PM
# @FileName: Base.py
# @Software: PyCharm
# @Github    ：sudoskys
import rtoml


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

    def parseFile(self, paths):
        data = rtoml.load(open(paths, 'r'))
        self.config = Tool().dictToObj(data)
        return self.config

    def parseDict(self, data):
        self.config = Tool().dictToObj(data)
        return self.config
