import logging
from logging.handlers import RotatingFileHandler
import os
from shared.log import LogConfig

class QQBotAPIError(Exception):
    """QQ机器人API请求失败时抛出的异常"""
    def __init__(self, message, response=None):
        super().__init__(message)
        self.response = response
        LogConfig().get_logger(__name__).error(f"{message} Response: {response}")
        
class DataNotFoundInDataBaseError(Exception):
    def __init__(self, message):
        super().__init__(message)
        logger = LogConfig().get_logger("DataBase")
        logger.error(message)
