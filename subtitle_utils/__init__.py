# -*- coding: utf-8 -*-
# @Time    : 12/29/22 10:06 PM
# @FileName: convert.py
# @Software: PyCharm
# @Github    ：sudoskys
import json
import os
from typing import Union

import pathlib
import pysrt
from loguru import logger

# Child
from .BccConverter import BccConvert
from .AssConverter import AssConvert
from pydantic import BaseModel

about = None


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


class _Converter(object):
    def __init__(self):
        pass

    def srt2bcc(self,
                strs: Union[str],
                **kwargs
                ):
        result = None
        try:
            result = BccConvert().srt2bcc(files=strs, about=about)
            result = json.dumps(result, ensure_ascii=False, indent=None)
        except Exception as e:
            logger.error(e)
        return result


class Returner(BaseModel):
    status: bool = False
    pre: str
    aft: str
    msg: str = "Unknown"
    data: str = None


def FormatConverter(pre: str, aft: str,
                    files: str = "",
                    strs: str = "",
                    **kwargs
                    ) -> Returner:
    """
    转换管线
    :param strs: 必须是字符串
    :param pre: 先前的格式
    :param aft: 转换为什么
    :param files: 必须是文件绝对路径
    :return: class Returner
    """
    __kira = _Converter()
    _aft = f"to{aft}"
    _to_table = {
        "tosrt": {
        },
        "tobcc": {
            "srt": __kira.srt2bcc,
        },
        "toass": {
        },
    }
    if not strs and not files:
        return Returner(status=False, pre=pre, aft=aft, msg="Miss arg")
    # 检查类型
    if not _to_table.get(_aft):
        return Returner(status=False, pre=pre, aft=aft, msg="Unsupported to format")
    if not _to_table.get(_aft).get(pre):
        return Returner(status=False, pre=pre, aft=aft, msg="Unsupported from format")
    # 同步数据
    import tempfile
    tmp = tempfile.NamedTemporaryFile(delete=True)
    # 调用函数
    func = _to_table[_aft][pre]
    try:
        if not files:
            _b = bytes(strs, 'utf8')
            tmp.write(_b)
            tmp.seek(0)
            files = tmp.name
        if not strs:
            with pathlib.Path(files).open("r") as ori:
                strs = ori.read()
        _result = func(strs=strs, files=files, **kwargs)
    except Exception as e:
        logger.error(f"{pre}->{aft}:{e}")
        return Returner(status=False, pre=pre, aft=aft, msg="Error occur")
    else:
        return Returner(status=True, pre=pre, aft=aft, data=_result, msg="")
    finally:
        tmp.close()
