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

    def merge_timeline(self, list1):
        # 定义一个字典用于存储新生成的list元素
        result = {}
        for item in list1:
            # 判断该元素是否在字典中存在
            if item["from"] in result.keys():
                # 如果存在，则修改to和content
                result[item["from"]]["to"] = max(result[item["from"]]["to"], item["to"])
                result[item["from"]]["content"] += "/n" + item["content"]
            else:
                # 如果不存在就直接添加
                result[item["from"]] = {
                    "from": item["from"],
                    "to": item["to"],
                    "location": item["location"],
                    "content": item["content"]
                }
        final = []
        for key in result.keys():
            final.append(result[key])
        return final

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
