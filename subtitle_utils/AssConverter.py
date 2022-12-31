# -*- coding: utf-8 -*-
# @Time    : 12/30/22 2:54 PM
# @FileName: AssConverter.py
# @Software: PyCharm
# @Github    ：sudoskys
import re
from pathlib import Path
from pyasstosrt import Subtitle


class AssUtils(object):
    @staticmethod
    def defultHeader() -> str:
        return """[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,20,&H00FFFFFF,&HF0000000,&H00000000,&HF0000000,1,0,0,0,100,100,0,0.00,1,1,0,2,30,30,10,134

[Events]
Format: Layer, Start, End, Style, Actor, MarginL, MarginR, MarginV, Effect, Text"""

    @staticmethod
    def srt_timestamps(content: str) -> list:
        """ 获取时间轴存于字典中 """
        timestamps = []
        for ts in re.findall(r'\d{2}:\d{2}:\d{2},\d{3}.+\d{2}:\d{2}:\d{2},\d{3}', content):
            ts = ts.split(' --> ')
            timestamps.append(ts)
        return timestamps

    @staticmethod
    def srt_subtitles(content: str) -> list:
        # 通过分割时间轴获取字幕存储于列表中返回
        content = content.replace('\ufeff', '')
        _subtitles = re.split(r'\d{2}:\d{2}:\d{2},\d{3}.+\d{2}:\d{2}:\d{2},\d{3}', content)
        subtitles = []
        for s in range(1, len(_subtitles)):
            subtitle = re.sub(r'(\r\n\r\n\d+\r\n)|(^\r\n)|(^\n)|(\n\n\d+\n)|(\u200e)', '', _subtitles[s])
            subtitle = re.sub('(\r\n)|\n', ' ', subtitle)
            subtitles.append(subtitle)
        return subtitles

    @staticmethod
    def ass_content(timestamps: list, subtitles: list, header: str) -> str:
        content = header + '\n'
        body = {
            'dialogue': 'Dialogue: ',
            'front_time': '',
            'behind_time': '',
            'default': 'Default',
            'ntp': 'NTP',
            '0000': '0000',
            'sub': ',',
        }
        count = len(subtitles)
        for c in range(count):
            start = timestamps[c][0]  # 获取当前字幕起始时间
            start = start[:1] + ',' + start[1:8] + '.' + start[-2:]
            end = timestamps[c][1]  # 获取当前字幕结束时间
            end = end[1:8] + '.' + end[-2:]
            timeline = ','.join([start, end])  # 合成时间轴

            subtitle = subtitles[c]  # 获取当前字幕

            list2str = [  # 字幕列表格式化
                body['dialogue'] + timeline,
                body['default'],
                body['ntp'],
                body['0000'],
                body['0000'],
                body['0000'] + ',',
                subtitle]

            content += ','.join(list2str)
            content += '\n'
        return content


class AssConvert(object):

    def ass2srt(self, files: str) -> str:
        path = Path(files)
        sub = Subtitle(path)
        dialog = sub.export(output_dialogues=True)
        _result = []
        for dialogue in dialog:
            _result.append(str(dialogue))
        return "".join(_result)

    def srt2ass(self, strs: str, header: str = "") -> str:
        header = header if header else AssUtils.defultHeader()
        timestamps = AssUtils.srt_timestamps(strs)
        subtitles = AssUtils.srt_subtitles(strs)
        content = AssUtils.ass_content(timestamps, subtitles, header)
        return content

# res = AssConvert().ass2srt(files="../test/sub.ass")
# print(res)
