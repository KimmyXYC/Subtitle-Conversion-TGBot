# -*- coding: utf-8 -*-
# @Time    : 9/22/22 11:04 PM
# @FileName: Event.py
# @Software: PyCharm
# @Github    ：sudoskys
import json
import os
import pathlib
from typing import Union

import chardet
from telebot import types, util
from telebot.async_telebot import AsyncTeleBot

import subtitle_utils

from loguru import logger

from utils.Base import random_filename, filter_str
from utils.Setting import get_app_config


def convert2bcc(file_type: str, files: Union[str]):
    result = None
    try:
        if file_type == ".srt":
            result = subtitle_utils.BccConvert().srt2bcc(files=files, about=get_app_config()["Info"]["about"])
            result = json.dumps(result, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(e)
    return result


async def BccConverter(bot: AsyncTeleBot, message: types.Message):
    user = message.from_user.id
    fileID = message.document.file_id
    file_size = message.document.file_size
    file_name = message.document.file_name if message.document.file_name else ""
    file_type = os.path.splitext(file_name)[-1]
    file_name: str
    uid = f"{user}_{random_filename(file_name)}"
    if file_size > 1048576 * 2:
        return False, "Too Large"
    if file_type not in [".srt"]:
        return False, "Unsupported Type"
    file_info = await bot.get_file(fileID)
    down_file = await bot.download_file(file_info.file_path)
    encode = chardet.detect(down_file).get("encoding")
    if not encode:
        return False, "Unknown File Format"
    try:
        content = down_file.decode(encode)
    except Exception as e:
        logger.error(f"{user}:{e}")
        return False, "Unknown File Format"
    else:
        _result_str = convert2bcc(file_type=file_type, files=content)
    if not _result_str:
        return False, "Failed,Maybe Error?"
    return True, _result_str


async def ToBcc(bot: AsyncTeleBot, message: types.Message, config):
    if message.document:
        user = message.from_user.id
        file_name = message.document.file_name
        if len(file_name) > 120:
            return
        success, result = await BccConverter(bot, message)
        if not success:
            return await bot.reply_to(message, result)
        result: str
        # 发送
        filename = f"{filter_str(file_name)}.json"
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
    await bot.reply_to(message, "发送SRT字幕文件")
