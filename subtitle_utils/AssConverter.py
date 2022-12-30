# -*- coding: utf-8 -*-
# @Time    : 12/30/22 2:54 PM
# @FileName: AssConverter.py
# @Software: PyCharm
# @Github    ：sudoskys
from pathlib import Path

from pyasstosrt import Subtitle


class AssConvert(object):
    def ass2srt(self, files: str):
        path = Path(files)
        sub = Subtitle(path)
        dialog = sub.export(output_dialogues=True)
        _result = []
        for dialogue in dialog:
            _result.append(str(dialogue))
        return "".join(_result)

# res = AssConvert().ass2srt(files="../test/sub.ass")
# print(res)
