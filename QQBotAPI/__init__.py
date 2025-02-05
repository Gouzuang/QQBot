import logging
from logging.handlers import RotatingFileHandler
import os
from .QQBotHttp import QQBotHttp
from .message import message
from .data import data
from .person import Person, Group

__all__ = ['QQBotHttp', 'QQBotAPIError', 'QQBot', 'message', 'data', 'Person', 'Group']

class QQBotAPIError(Exception):
    """QQ机器人API请求失败时抛出的异常"""
    
    @staticmethod
    def _get_logger():
        """获取错误日志记录器"""
        logger = logging.getLogger('QQBotAPI.Error')
        if not logger.handlers:
            # 设置日志格式
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            
            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            
            # 文件处理器
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

class QQBot:
    def __init__(self,url,client_id=0):
        self.api = QQBotHttp(url,client_id)
        self.logger = self._setup_logger()
        
        self.logger.info("Initializing QQBotHttp with URL: %s", url)
        self.qq_id = self.api.get_login_info().get('qq')
        self.nickname = self.api.get_login_info().get('nickname')
        self.friend_list = self.get_friend_list()
        
        self.logger.info("Bot initialized. QQ ID: %s, Nickname: %s", self.qq_id, self.nickname)
        
    def _setup_logger(self):
        """设置独立的日志系统"""
        logger = logging.getLogger(f'QQBotHttp_{id(self)}')  # 使用实例ID确保唯一性
        logger.setLevel(logging.INFO)
        
        # 确保logger不会重复添加handler
        if not logger.handlers:
            # 控制台输出
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
            
            # 文件输出
            log_dir = 'logs'
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            file_handler = RotatingFileHandler(
                os.path.join(log_dir, 'qqbot.log'),
                maxBytes=1024*1024,  # 1MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.INFO)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levellevel)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            
            # 防止日志向上层传递
            logger.propagate = False
            
        return logger
    
    #好友信息
    def get_user_info(self,user_id):
        if user_id in self.friend_list:
            return self.friend_list[self.friend_list.index(user_id)]
        else:
            info = self.api.get_stranger_info(user_id)
            return Person(user_id=user_id, nickname=info['nickname'])
    
    def get_friend_list(self):
        """获取好友列表
        
        Returns:
            List[Person]: 好友列表
        """
        friends = self.api.get_friend_list()
        friend_list = []
        for friend in friends:
            friend_list.append(Person(user_id=friend['user_id'], 
                                      nickname=friend['nickname'], 
                                      remark=friend['remark']
                                      ))
        return friend_list

    def send_private_message(self,user,message):
        """发送私聊消息
        
        Args:
            user (Union[int, Person]): 用户ID或Person对象
            message (List[message]): 消息内容
        """
        if isinstance(user, Person):
            user_id = user.user_id
        else:
            user_id = user
        messages = []
        for msg in message:
            messages.append(msg.json())
        self.api.send_private_message(user_id,messages)
        
    def send_group_message(self,group,message):
        """发送群消息
        
        Args:
            group (Union[int, Group]): 群ID或Group对象
            message (List[message]): 消息内容
        """
        if isinstance(group, Group):
            group_id = group.group_id
        else:
            group_id = group
        messages = []
        for msg in message:
            messages.append(msg.json())
        self.api.send_group_message(group_id,messages)