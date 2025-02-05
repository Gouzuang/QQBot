import logging
from logging.handlers import RotatingFileHandler
import os

class QQBotAPIError(Exception):
    """QQ机器人API请求失败时抛出的异常"""
    
    @staticmethod
    def _get_logger():
        """获取错误日志记录器"""
        logger = logging.getLogger('QQBotAPI.Error')
        if not logger.handlers:
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            
            log_dir = 'logs'
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            file_handler = RotatingFileHandler(
                os.path.join(log_dir, 'qqbot_error.log'),
                maxBytes=1024*1024,
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
            logger.setLevel(logging.ERROR)
            logger.propagate = False
            
        return logger

    def __init__(self, message, response=None):
        super().__init__(message)
        self.response = response
        self._get_logger().error(f"{message} Response: {response}")