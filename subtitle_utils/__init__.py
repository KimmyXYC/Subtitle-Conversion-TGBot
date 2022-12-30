# -*- coding: utf-8 -*-
# @Time    : 12/29/22 10:06 PM
# @FileName: convert.py
# @Software: PyCharm
# @Github    ：sudoskys
import os

import pysrt

from .BccConverter import BccConvert


class SrtParse(object):
    def __init__(self):
        pass

    def parse(self, files):
        path = files if files else ""
        if os.path.exists(path):
            subs = pysrt.open(path=files)
        else:
            subs = pysrt.from_string(source=files)
        return subs
