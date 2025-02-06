import logging
from logging.handlers import RotatingFileHandler
import os
from typing import List

from QQBotAPI import DataManager
from .QQBotHttp import QQBotHttp
from .message import *
from .data import QQ_FACE_DISCRIPTION
from .person import Person, Group
from .errors import QQBotAPIError

class QQBot:
    def __init__(self,url,client_id=0):
        # 确保 URL 包含协议前缀
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        self.api = QQBotHttp(url,client_id)
        self.qq_id = "Temp"
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("Initializing QQBotHttp with URL: %s", url)
        self.qq_id = self.api.get_login_info().get('user_id')
        self.nickname = self.api.get_login_info().get('nickname')
        self.friend_list = self.get_friend_list()
        
        self.logger = logging.getLogger(__name__ + "." + self.qq_id)
        
        self.MessageManager = DataManager.MessageManager(self.qq_id)
    
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

    def send_private_message(self,user:Union[int,Person],message):
        """发送私聊消息
        
        Args:
            user (Union[int, Person]): 用户ID或Person对象
            message (List[message]): 消息内容
        """
        if isinstance(user, Person):
            user_id = user.get_user_id()
        else:
            user_id = user
        messages = []
        for msg in message:
            messages.append(msg.get_json())
        self.api.send_private_message(messages,user_id)
        
    def send_group_message(self,group,message):
        """发送群消息
        
        Args:
            group (Union[int, Group]): 群ID或Group对象
            message (List[message]): 消息内容
        """
        if isinstance(group, Group):
            group_id = group.get_group_id()
        else:
            group_id = group
        messages = []
        for msg in message:
            messages.append(msg.get_json())
        self.api.send_group_message(messages,group_id)