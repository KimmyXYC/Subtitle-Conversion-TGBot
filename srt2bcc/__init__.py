# -*- coding: utf-8 -*-
# @Time    : 12/29/22 10:06 PM
# @FileName: convert.py
# @Software: PyCharm
# @Github    ：sudoskys

import re
import os
import json
import pysrt
import pyvtt
from datetime import datetime
from loguru import logger
import sys

logger.remove()
handler_id = logger.add(sys.stderr, level="TRACE")


class BccConvert(object):
    def __init__(self, file_path: str):
        self.filepath = file_path
        self.item = {
            "from": 0,
            "to": 0,
            "location": 2,
            "content": "",
        }

    def merge_timeline(self, bcc_raw: list):
        _compiles = []
        if len(bcc_raw) < 2:
            return bcc_raw
        _all_right = False
        _index = 0
        while not _all_right:
            for it in range(_index, len(bcc_raw) - 1):
                _all_right = True
                _index = it
                item = bcc_raw[it]
                next_item = bcc_raw[it + 1]
                end_time = item["to"]
                next_start_time = next_item["from"]
                # 下一个对象的起始掉到本对象界中，就生产新对象并交换初始化
                if next_start_time < end_time:
                    _start = bcc_raw[it]["from"]
                    bcc_raw[it]["to"] = next_start_time
                    bcc_raw[it + 1]["from"] = end_time
                    if _start != next_start_time:
                        cont = f"{next_item['content']}\n{item['content']}"
                        _compiles.append(bcc_raw[it])
                        logger.trace(bcc_raw[it])
                    else:
                        cont = f"{item['content']}\n{next_item['content']}"
                    _compiles.append(
                        {"from": next_start_time,
                         "to": end_time,
                         "location": 2,
                         "content": cont
                         }
                    )
                    logger.trace({"from": next_start_time,
                                  "to": end_time,
                                  "location": 2,
                                  "content": cont
                                  })
                    _all_right = False
                    break
                elif next_start_time == end_time:
                else:
                    if _compiles:
                        if bcc_raw[it]["from"] >= _compiles[-1]["to"]:
                            _compiles.append(bcc_raw[it])
                            logger.trace(bcc_raw[it])
                    else:
                        _compiles.append(bcc_raw[it])
                        logger.trace(bcc_raw[it])
        _compiles.append(bcc_raw[len(bcc_raw) - 1])
        _return = []
        for it in _compiles:
            _return.append(it)
        print(_return)
        return _return

    def process_body(self, subs):
        _origin = [
            {
                "from": sub.start.ordinal / 1000,
                "to": sub.end.ordinal / 1000,
                "location": 2,
                "content": sub.text,
            }
            for sub in subs
        ]
        print(_origin)
        _fix = self.merge_timeline(_origin)
        return _fix

    def srt2bcc(self):
        """
        srt2bcc 将 srt 转换为 bcc B站字幕格式
        :return:
        """
        subs = pysrt.open(path=self.filepath)
        bcc = {
            "font_size": 0.4,
            "font_color": "#FFFFFF",
            "background_alpha": 0.5,
            "background_color": "#9C27B0",
            "Stroke": "none",
            "body": self.process_body(subs)
        }
        return bcc if subs else {}

    def vtt2bcc(self, threshold=0.1, word=True):
        path = self.filepath if self.filepath else ""
        if os.path.exists(path):
            subs = pyvtt.open(path)
        else:
            subs = pyvtt.from_string(path)
        # NOTE 按照 vtt 的断词模式分隔 bcc
        caption_list = []
        if not word:
            caption_list = [
                {
                    "from": sub.start.ordinal / 1000,
                    "to": sub.end.ordinal / 1000,
                    "location": 2,
                    "content": sub.text_without_tags.split("\n")[-1],
                }
                for sub in subs
            ]
        else:
            for i, sub in enumerate(subs):
                text = sub.text

                start = sub.start.ordinal / 1000
                end = sub.end.ordinal / 1000
                try:
                    idx = text.index("<")
                    pre_text = text[:idx]
                    regx = re.compile(r"<(.*?)><c>(.*?)</c>")
                    for t_str, match in regx.findall(text):
                        pre_text += match
                        t = datetime.strptime(t_str, r"%H:%M:%S.%f")
                        sec = (
                                t.hour * 3600
                                + t.minute * 60
                                + t.second
                                + t.microsecond / 10 ** len((str(t.microsecond)))
                        )
                        final_text = pre_text.split("\n")[-1]

                        if caption_list and (
                                sec - start <= threshold
                                or caption_list[-1]["content"] == final_text
                        ):
                            caption_list[-1].update(
                                {
                                    "to": sec,
                                    "content": final_text,
                                }
                            )
                        else:
                            caption_list.append(
                                {
                                    "from": start,
                                    "to": sec,
                                    "location": 2,
                                    "content": final_text,
                                }
                            )
                        start = sec
                except:
                    final_text = sub.text.split("\n")[-1]
                    if caption_list and caption_list[-1]["content"] == final_text:
                        caption_list[-1].update(
                            {
                                "to": end,
                                "content": final_text,
                            }
                        )
                    else:
                        if caption_list and end - start < threshold:
                            start = caption_list[-1]["to"]
                        caption_list.append(
                            {
                                "from": start,
                                "to": end,
                                "location": 2,
                                "content": final_text,
                            }
                        )

        # print(len(caption_list))
        # NOTE 避免超出视频长度
        last = caption_list[-1]
        last["to"] = last.get("from") + 0.1
        bcc = {
            "font_size": 0.4,
            "font_color": "#FFFFFF",
            "background_alpha": 0.5,
            "background_color": "#9C27B0",
            "Stroke": "none",
            "body": caption_list,
        }

        return bcc if subs else {}


