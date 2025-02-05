import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

class LogConfig:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LogConfig, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not LogConfig._initialized:
            self._setup_log_directory()
            LogConfig._initialized = True
            
    def _setup_log_directory(self):
        """设置日志目录和全局日志文件路径"""
        self.log_dir = 'logs'
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file_path = os.path.join(self.log_dir, f'app_{timestamp}.log')
        
        # 配置根日志记录器
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        file_handler = logging.FileHandler(self.log_file_path, encoding='utf-8')
        file_handler.setFormatter(formatter)
        
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        
        logging.basicConfig(
            level=logging.DEBUG,
            handlers=[file_handler, stream_handler]
        )
    
    def get_logger(self, name, extra_formatter=None):
        """获取配置好的日志记录器
        
        Args:
            name (str): 日志记录器名称
            extra_formatter (dict, optional): 额外的格式化参数
            
        Returns:
            logging.Logger: 配置好的日志记录器
        """
        logger = logging.getLogger(name)
        
        if not logger.handlers:
            # 基本格式
            format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            
            # 添加额外的格式化参数
            if extra_formatter:
                formatter = logging.Formatter(format_str, defaults=extra_formatter)
            else:
                formatter = logging.Formatter(format_str)
            
            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            
            # 文件处理器
            file_handler = RotatingFileHandler(
                self.log_file_path,
                maxBytes=1024*1024,
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
            logger.setLevel(logging.DEBUG)
            logger.propagate = False
            
        return logger
