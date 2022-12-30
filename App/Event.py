# -*- coding: utf-8 -*-
# @Time    : 9/22/22 11:04 PM
# @FileName: Event.py
# @Software: PyCharm
# @Github    ：sudoskys
from loguru import logger


async def SRT(bot, message, config):
    if message.document:
        file_size = message.document.file_size
        print(message.document.mime_type)
        if file_size < 256000:
            fileID = message.document.file_id
            file_info = bot.get_file(fileID)
            print(file_info)
            return
            down_file = bot.download_file(file_info.file_path)
            with open("", 'wb') as new_file:
                new_file.write(down_file)
            # bot.reply_to(message, target)
        else:
            bot.reply_to(message, '文件过大')


async def Start(bot, message, config):
    await bot.reply(message, "发送SRT字幕文件")
