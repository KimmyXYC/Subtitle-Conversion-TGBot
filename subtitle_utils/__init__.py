# -*- coding: utf-8 -*-
# @Time    : 12/29/22 10:06 PM
# @FileName: convert.py
# @Software: PyCharm
# @Github    ：sudoskys

import re
import os

import pyvtt
import pysrt

from typing import Union
from datetime import datetime
from loguru import logger
import sys

logger.remove()
handler_id = logger.add(sys.stderr, level="TRACE")


class BccConvert(object):
    def __init__(self):
        self.item = {
            "from": 0,
            "to": 0,
            "location": 2,
            "content": "",
        }

    def merge_timeline(self, time_line: list):
        """
        防止时间码重合，压扁时间轴
        :param time_line:
        :return:
        """
        # 制作爆破点
        _time_dot = {}
        for item in time_line:
            _start = item["from"]
            _end = item["to"]
            _content = item["content"]
            _uid = _start + _end
            import uuid
            uid1 = uuid.uuid1()
            uid2 = uuid.uuid1()
            uid = uuid.uuid1()
            _time_dot[uid1.hex] = {"time": _start, "type": "start", "content": _content, "group": uid}
            _time_dot[uid2.hex] = {"time": _end, "type": "end", "content": _content, "group": uid}

        # 查找当前点的字幕。
        def sub_title_now(dot: float):
            sub_title_n = []
            for it in time_line:
                if it["from"] <= dot < it["to"]:
                    sub_title_n.append(it["content"])
            return "\n".join(sub_title_n)

        # 开始遍历时间轴划分Start End
        tmp_cap = []
        _sorted_timeline = sorted(_time_dot.items(), key=lambda x: x[1]["time"], reverse=False)
        for key, time in _sorted_timeline:
            _type = time["type"]
            _time = time["time"]
            _group = time["group"]
            _content = time["content"]
            tmp_cap.append(_time)
        _result = []
        for dot in range(0, len(tmp_cap) - 1):
            _now = tmp_cap[dot]
            _next = tmp_cap[dot + 1]
            _text = sub_title_now(_now)
            if not _text:
                continue
            _from = _now
            _to = _next
            _item = {
                "from": _from,
                "to": _to,
                "location": 2,
                "content": _text,
            }
            _result.append(_item)

        # 归并内容
        def merge(timeline: list):
            merged = False
            for it in range(0, len(timeline) - 1):
                now = timeline[it]
                ext = timeline[it + 1]
                if now["to"] == ext["from"]:
                    if now["content"] == ext["content"]:
                        merged = True
                        now["to"] = ext["to"]
                        timeline.remove(ext)
                        break
            if merged:
                return merge(timeline)
            else:
                return timeline

        return merge(_result)

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
        _fix = self.merge_timeline(_origin)
        return _fix

    def srt2bcc(self, files: Union[str]):
        """
        srt2bcc 将 srt 转换为 bcc B站字幕格式
        :return:
        """
        path = files if files else ""
        if os.path.exists(path):
            subs = pysrt.open(path=files)
        else:
            subs = pysrt.from_string(source=files)
        bcc = {
            "font_size": 0.4,
            "font_color": "#FFFFFF",
            "background_alpha": 0.5,
            "background_color": "#9C27B0",
            "Stroke": "none",
            "body": self.process_body(subs)
        }
        return bcc if subs else {}

    def vtt2bcc(self, files, threshold=0.1, word=True):
        path = files if files else ""
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