# -*- coding: utf-8 -*-
# @Time    : 12/30/22 3:11 PM
# @FileName: test_convert.py
# @Software: PyCharm
# @Github    ：sudoskys
from pathlib import Path

from pyasstosrt import Subtitle

path = Path('.sub.ass')
sub = Subtitle(path)
sub.export()
