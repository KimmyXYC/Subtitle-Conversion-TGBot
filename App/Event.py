# -*- coding: utf-8 -*-
# @Time    : 9/22/22 11:04 PM
# @FileName: Event.py
# @Software: PyCharm
# @Github    ：sudoskys
import json
import os
import pathlib
from typing import Union, Any

import chardet
from telebot import types, util
from telebot.async_telebot import AsyncTeleBot

import subtitle_utils

from loguru import logger

from utils.Base import random_filename, filter_str, FileInfo
from utils.Setting import get_app_config

command_match = ["srt", "bcc", "ass", "vtt"]


def match_to_what(text: str) -> Union[tuple, None]:
    if not text:
        return False, "What format you want convert to? please note it in file caption.\nUse lowercase three letters."
    for it in command_match:
        if it in text:
            return True, it
    return False, "Maybe not a subtitle file?"


async def GetFile(bot: AsyncTeleBot, message: types.Message) -> FileInfo:
    user = message.from_user.id
    fileID = message.document.file_id
    file_size = message.document.file_size
    file_name = message.document.file_name if message.document.file_name else ""
    file_type = os.path.splitext(file_name)[-1][1:] if "." in file_name else None
    file_name: str
    uid = f"{user}_{random_filename(file_name)}"
    if not file_type:
        return FileInfo(status=False, type=file_type, msg="Unsupported Type", result=None, size=file_size)
    if file_size > 1048576 * 2:
        return FileInfo(status=False, type=file_type, msg="Too Large", result=None, size=file_size)
    file_info = await bot.get_file(fileID)
    down_file = await bot.download_file(file_info.file_path)
    encode = chardet.detect(down_file).get("encoding")
    if not encode:
        return FileInfo(status=False, type=file_type, msg="Unknown File Format", result=None, size=file_size)
    try:
        content = down_file.decode(encode)
    except Exception as e:
        logger.error(f"{user}:{e}")
        return FileInfo(status=False, type=file_type, msg="Unknown File Format", result=None, size=file_size)
    else:
        return FileInfo(status=True, type=file_type, msg="", result=content, size=file_size)


async def Convert(bot: AsyncTeleBot, message: types.Message, config) -> Any:
    _order = message.caption
    status, _to_type = match_to_what(_order)
    if not status:
        return await bot.reply_to(
            message,
            _to_type
        )
    # 获取到将要
    if message.document:
        user = message.from_user.id
        file_name = message.document.file_name
        if len(file_name) > 120:
            return "Too long...."
        if ".tw" in file_name or ".tc" in file_name or "cht" in file_name:
            subtitle_utils.about = get_app_config()["Info"]["about_tw"]
        else:
            subtitle_utils.about = get_app_config()["Info"]["about"]
        file_group = await GetFile(bot, message)
        file_group: FileInfo
        if not file_group.status:
            return await bot.reply_to(message, file_group.msg)
        # 转换转圈圈
        _result_group = subtitle_utils.FormatConverter(pre=file_group.type, aft=_to_type, strs=file_group.result)
        _result_group: subtitle_utils.Returner
        if not _result_group.status:
            return await bot.reply_to(message, _result_group.msg)
        result: str
        result = _result_group.data
        # 发送
        filename = f"{filter_str(file_name)}.{_result_group.aft}"
        try:
            with open(filename, 'w+') as f:
                f.write(result)
            await bot.send_document(caption="",
                                    chat_id=message.chat.id,
                                    reply_to_message_id=message.id,
                                    document=open(filename, "rb")
                                    )
            logger.success(f"Send:--time {message.date} --userid {user} --name {file_name}")
            return
        except Exception as e:
            logger.error(f"SendFail:{e}")
            return await bot.reply_to(message, "Error Occur")
        finally:
            pathlib.Path(filename).unlink(missing_ok=True)
            return


async def Start(bot: AsyncTeleBot, message: types.Message, config):
    await bot.reply_to(
        message,
        "Send the subtitle file with the format you need to convert in the caption (lowercase 3 letters)."
    )


async def Help(bot: AsyncTeleBot, message: types.Message, config):
    method = subtitle_utils.SeeAvailableMethods()
    _support = "\n".join(method)
    _url = "https://github.com/KimmyXYC/Subtitle-Conversion-TGBot"
    _use = "Send the subtitle file with the format you need to convert in the caption (lowercase 3 letters)."
    await bot.reply_to(
        message,
        f"-Multi-format subtitle converter-\n{_use}\nNow support\n{_support}\n\nBy {_url}",
        disable_web_page_preview=True,
    )
