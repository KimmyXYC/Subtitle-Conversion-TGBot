# -*- coding: utf-8 -*-
# @Time    : 9/22/22 10:07 PM
# @FileName: main.py
# @Software: PyCharm
# @Github    ：sudoskys
from pathlib import Path
from utils.Base import ReadConfig
from App.Controller import BotRunner
from loguru import logger
import sys

logger.remove()
handler_id = logger.add(sys.stderr, level="INFO")
logger.add(sink='run.log',
           format="{time} - {level} - {message}",
           level="INFO",
           rotation="20 MB",
           enqueue=True)

config = ReadConfig().parseFile(str(Path.cwd()) + "/Config/app.toml")
App = BotRunner(config)
App.run()
