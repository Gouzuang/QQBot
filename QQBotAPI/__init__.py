import time
import requests
import logging
import os
from logging.handlers import RotatingFileHandler

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

class QQBotHttp():
    def __init__(self,url,client_id=0):
        self._url = url
        self._client_id = client_id
        
        # 配置独立的日志系统
        self.logger = self._setup_logger()
        
        self.logger.info("Initializing QQBotHttp with URL: %s", url)
        self._qq_id = self.get_login_info().get('user_id')
        self._nickname = self.get_login_info().get('nickname')
        
        self.logger.info("Bot initialized. QQ ID: %s, Nickname: %s", self._qq_id, self._nickname)

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

    #Bot 账号
    def get_login_info(self):
        """获取QQ机器人的登录信息。

        返回:dict
             user_id	int64	QQ 号
            nickname	string	QQ 昵称

        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
        """
        self.logger.info("Getting login info...")
        url = self._url + "/get_login_info"
        try:
            response = requests.get(url).json()
            if response.get('status') == 'ok':
                self.logger.info("Successfully got login info")
                return response
            raise QQBotAPIError("API request failed", response)
        except requests.RequestException as e:
            raise QQBotAPIError(f"Connection failed: {str(e)}")
    
    #好友信息
    def get_stranger_info(self,user_id,no_cache=False):
        """获取陌生人信息。
        
        参数:
            user_id (int): QQ号
            no_cache (bool, optional): 是否不使用缓存. 默认为False.
            
        返回:
            dict: 包含以下字段:
            - user_id (int): QQ号
            - nickname (str): 昵称 
            - sex (str): 性别('male'/'female'/'unknown')
            - age (int): 年龄
            - qid (str): qid ID身份卡
            - level (int): 等级
            - login_days (int): 登录天数
            
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
        """
        self.logger.info("Getting stranger info for user %s", user_id)
        url = self._url + "/get_stranger_info"
        params = {
            'user_id': user_id,
            'no_cache': no_cache
        }
        try:
            response = requests.get(url, params=params).json()
            if response.get('status') == 'ok':
                self.logger.info("Successfully got stranger info for user %s", user_id)
                return response
            raise QQBotAPIError("API request failed", response)
        except requests.RequestException as e:
            raise QQBotAPIError(f"Connection failed: {str(e)}")
        
    def get_friend_list(self):
        """获取好友列表。
        
        返回:
            list: 包含好友信息的数组，每个元素包含：
                - user_id (int64): QQ 号
                - nickname (string): 昵称
                - remark (string): 备注名
                
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
        """
        url = self._url + "/get_friend_list"
        self.logger.debug("Getting friend list...")
        try:
            response = requests.get(url).json()
            if response.get('status') == 'ok':
                self.logger.info("Successfully got friend list")
                return response.get('data')
            raise QQBotAPIError("API request failed", response)
        except requests.RequestException as e:
            raise QQBotAPIError(f"Connection failed: {str(e)}")
        
    def get_unidirectional_friend_list(self):
        """获取单向好友列表。
        
        返回:
            list: 包含单向好友信息的数组，每个元素包含：
            - user_id (int64): QQ号
            - nickname (string): 昵称 
            - source (string): 来源
            
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
        """
        url = self._url + "/get_unidirectional_friend_list"
        self.logger.debug("Getting unidirectional friend list...")
        try:
            response = requests.get(url).json()
            if response.get('status') == 'ok':
                self.logger.info("Successfully got unidirectional friend list")
                return response.get('data')
            raise QQBotAPIError("API request failed", response)
        except requests.RequestException as e:
            raise QQBotAPIError(f"Connection failed: {str(e)}")
        
    #好友操作
    def delete_friend(self,user_id):
        """删除好友。
        
        参数:
            user_id (int): QQ号
            
        返回:
            bool: 是否成功删除好友
            
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
        """
        self.logger.info("Deleting friend %s", user_id)
        url = self._url + "/delete_friend"
        params = {
            'user_id': user_id
        }
        try:
            response = requests.get(url, params=params).json()
            if response.get('status') == 'ok':
                self.logger.info("Successfully deleted friend %s", user_id)
                return True
            raise QQBotAPIError("API request failed", response)
        except requests.RequestException as e:
            raise QQBotAPIError(f"Connection failed: {str(e)}")
        
    def delete_unidirectional_friend(self,user_id):
        """删除单向好友。
        
        参数:
            user_id (int): QQ号
            
        返回:
            bool: 是否成功删除单向好友
            
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
        """
        self.logger.info("Deleting unidirectional friend %s", user_id)
        url = self._url + "/delete_unidirectional_friend"
        params = {
            'user_id': user_id
        }
        try:
            response = requests.get(url, params=params).json()
            if response.get('status') == 'ok':
                self.logger.info("Successfully deleted unidirectional friend %s", user_id)
                return True
            raise QQBotAPIError("API request failed", response)
        except requests.RequestException as e:
            raise QQBotAPIError(f"Connection failed: {str(e)}")
        
    #消息
    def send_private_message(self,message,user_id):
        """通过QQ机器人API向指定用户发送私聊消息。
        
        参数:
            message (str): 要发送的消息内容
            user_id (int): 接收消息的QQ用户号

        返回: dict
            message_id(int):消息 ID

        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
        """
        self.logger.info("Sending private message to user %s", user_id)
        url = self._url + "/send_private_msg"
        params = {
            'user_id': user_id,
            'message': message
        }
        for attempt in range(3):
            try:
                self.logger.debug("Attempt %s to send private message", attempt + 1)
                response = requests.get(url, params=params).json()
                if response.get('status') == 'ok':
                    self.logger.info("Successfully sent private message to user %s", user_id)
                    return response
                time.sleep(1)
            except requests.RequestException as e:
                if attempt == 2:
                    raise QQBotAPIError(f"Connection failed: {str(e)}")
                time.sleep(1)
                continue
        
        raise QQBotAPIError("API request failed after 3 attempts", response)
    
    def send_private_message_via_group(self,message,user_id,group_id):
        """通过QQ机器人API向群聊中的用户发送私聊消息。
        
        参数:
            message (str): 要发送的消息内容
            user_id (int): 接收消息的QQ用户号
            group_id (int): 群号

        返回: dict
            message_id(int):消息 ID

        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
        """
        self.logger.info("Sending private message to user %s via group %s", user_id, group_id)
        url = self._url + "/send_private_msg"
        params = {
            'user_id': user_id,
            'message': message,
            'group_id': group_id
        }
        for attempt in range(3):
            try:
                self.logger.debug("Attempt %s to send private message", attempt + 1)
                response = requests.get(url, params=params).json()
                if response.get('status') == 'ok':
                    self.logger.info("Successfully sent private message to user %s via group %s", user_id, group_id)
                    return response
                time.sleep(1)
            except requests.RequestException as e:
                if attempt == 2:
                    raise QQBotAPIError(f"Connection failed: {str(e)}")
                time.sleep(1)
                continue
        
        raise QQBotAPIError("API request failed after 3 attempts", response)
    
    def send_group_message(self,message,group_id):
        """通过QQ机器人API向指定群组发送消息。

        参数:
            message (str): 要发送的消息内容
            group_id (int): 接收消息的QQ群号

        返回:dict
            message_id(int):消息 ID

        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
        """
        self.logger.info("Sending group message to group %s", group_id)
        url = self._url + "/send_group_msg"
        params = {
            'group_id': group_id,
            'message': message
        }
        for attempt in range(3):
            try:
                self.logger.debug("Attempt %s to send group message", attempt + 1)
                response = requests.get(url, params=params).json()
                if response.get('status') == 'ok':
                    self.logger.info("Successfully sent group message to group %s", group_id)
                    return response
                time.sleep(1)
            except requests.RequestException as e:
                raise QQBotAPIError(f"Connection failed: {str(e)}")
        
        raise QQBotAPIError("API request failed after 3 attempts", response)

    def get_msg(self,message_id):
        """获取消息。
        
        参数:
            message_id (int): 消息ID
            
        返回:
            dict: 包含以下字段:
            - group (bool): 是否是群消息
            - group_id (int64): 群号(仅群消息)
            - message_id (int32): 消息id
            - real_id (int32): 消息真实id
            - message_type (str): 消息类型('group'或'private')
            - sender (dict): 发送者信息
                - nickname (str): 发送者昵称
                - user_id (int64): 发送者QQ号
            - time (int32): 发送时间
            - message (message): 消息内容
            - raw_message (message): 原始消息内容
            
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
        """
        self.logger.debug("Getting message %s", message_id)
        url = self._url + "/get_msg"
        params = {
            'message_id': message_id
        }
        try:
            response = requests.get(url, params=params).json()
            if response.get('status') == 'ok':
                self.logger.info("Successfully got message %s", message_id)
                return response.get('data')
            raise QQBotAPIError("API request failed", response)
        except requests.RequestException as e:
            raise QQBotAPIError(f"Connection failed: {str(e)}")
        
    def delete_msg(self,message_id):
        """撤回消息。

        参数:
            message_id (int): 消息ID

        返回:
            bool: 是否成功删除消息

        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
        """
        self.logger.info("Deleting message %s", message_id)
        url = self._url + "/delete_msg"
        params = {
            'message_id': message_id
        }
        try:
            response = requests.get(url, params=params).json()
            if response.get('status') == 'ok':
            self.logger.info("Successfully deleted message %s", message_id) 
            return True
            raise QQBotAPIError("API request failed", response)
        except requests.RequestException as e:
            raise QQBotAPIError(f"Connection failed: {str(e)}")
        
    def mark_msg_as_read(self,message_id):
        """标记消息已读。

        参数:
            message_id (int): 消息ID

        返回:
            bool: 是否成功标记消息已读

        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
        """
        self.logger.info("Marking message %s as read", message_id)
        url = self._url + "/mark_msg_as_read"
        params = {
            'message_id': message_id
        }
        try:
            response = requests.get(url, params=params).json()
            if response.get('status') == 'ok':
                self.logger.info("Successfully marked message %s as read", message_id)
                return True
            raise QQBotAPIError("API request failed", response)
        except requests.RequestException as e:
            raise QQBotAPIError(f"Connection failed: {str(e)}")
        
    def get_forward_msg(self,message_id):
        """获取合并转发消息。
        
        参数:
            message_id (int): 消息ID
            
        返回:
            list: MessageChain对象的数组
            
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
        """
        self.logger.debug("Getting forward message %s", message_id)
        url = self._url + "/get_forward_msg"
        params = {
            'message_id': message_id
        }
        try:
            response = requests.get(url, params=params).json()
            if response.get('status') == 'ok':
            self.logger.info("Successfully got forward message %s", message_id)
            messages = response.get('data', {}).get('messages', [])
            # TODO 解析消息
        except requests.RequestException as e:
            raise QQBotAPIError(f"Connection failed: {str(e)}")
        
    def send_group_forward_msg(self):
        pass
        #TODO 发送合并转发消息
        
    def send_private_forward_msg(self):
        pass
        #TODO 发送合并转发消息
        
    def get_group_msg_history(self):
        pass
        #TODO 获取群消息历史
    
    #图片
    
    #语音
    
    #文件
    
    #处理
    
    #群 信息
    
    #群 操作
    
    