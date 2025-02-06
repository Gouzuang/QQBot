import logging
from logging.handlers import RotatingFileHandler
import os

class QQBotAPIError(Exception):
    """QQ机器人API请求失败时抛出的异常"""
    def __init__(self, message, response=None):
        super().__init__(message)
        self.response = response
        logging.getLogger(__name__).error(f"{message} Response: {response}")
        
class DataNotFoundInDataBaseError(Exception):
    def __init__(self, message):
        super().__init__(message)
        logger = logging.getLogger(__name__)
        logger.error(message)
