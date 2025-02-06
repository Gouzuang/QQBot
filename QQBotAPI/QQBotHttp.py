import json
import time
from typing import Union
import requests
import logging
import os
from logging.handlers import RotatingFileHandler
from .errors import QQBotAPIError
from requests.exceptions import RequestException

class QQBotHttp():
    def __init__(self,url,client_id=0):
        self._url = url
        self._client_id = client_id
        
        self.logger = logging.getLogger('QQBot.HttpAPI')
        
        self.logger.info("Initializing QQBotHttp with URL: %s", url)
        self._qq_id = self.get_login_info().get('user_id')
        self._nickname = self.get_login_info().get('nickname')
        
        self.logger.info("Bot initialized. QQ ID: %s, Nickname: %s", self._qq_id, self._nickname)

    def _make_request(self, method: str, url: str, params=None, **kwargs) -> Union[dict, list]:
        """发送HTTP请求并处理响应
        
        参数:
            method (str): HTTP方法 ('GET' 或 'POST')
            url (str): 请求URL
            params (dict): 请求参数
            **kwargs: 传递给requests的其他参数
            
        重试3次后仍失败则抛出异常
        """
        for attempt in range(3):
            try:
                if method.upper() == 'POST':
                    # POST 请求直接发送 JSON 数据
                    response = requests.post(url, json=params).json()
                else:
                    # GET 请求使用 URL 参数
                    response = requests.get(url, params=params).json()
                    
                if response.get('status') == 'ok':
                    self.logger.debug(f"API '{url}' request successful: {json.dumps(response, indent=4, ensure_ascii=False)}")
                    return response.get('data')
                raise QQBotAPIError("API request failed", response)
            except (requests.RequestException, QQBotAPIError) as e:
                self.logger.warning(f"Request attempt {attempt + 1} failed: {str(e)}")
                if attempt == 2:
                    raise
                time.sleep(1)

    #Bot 账号
    def get_login_info(self):
        """获取QQ机器人的登录信息。

        返回:dict
             user_id	int64	QQ 号
            nickname	string	QQ 昵称

        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Getting login info...")
        url = self._url + "/get_login_info"
        return self._make_request('POST', url)
    
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
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Getting stranger info for user %s", user_id)
        url = self._url + "/get_stranger_info"
        params = {
            'user_id': user_id,
            'no_cache': no_cache
        }
        return self._make_request('POST', url, params=params)
        
    def get_friend_list(self):
        """获取好友列表。
        
        返回:
            list: 包含好友信息的数组，每个元素包含：
                - user_id (int64): QQ 号
                - nickname (string): 昵称
                - remark (string): 备注名
                
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        url = self._url + "/get_friend_list"
        self.logger.debug("Getting friend list...")
        return self._make_request('GET', url)
        
    def get_unidirectional_friend_list(self):
        """获取单向好友列表。
        
        返回:
            list: 包含单向好友信息的数组，每个元素包含：
            - user_id (int64): QQ号
            - nickname (string): 昵称 
            - source (string): 来源
            
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        url = self._url + "/get_unidirectional_friend_list"
        self.logger.debug("Getting unidirectional friend list...")
        return self._make_request('POST', url)
        
    #好友操作
    def delete_friend(self,user_id):
        """删除好友。
        
        参数:
            user_id (int): QQ号
            
        返回:
            bool: 是否成功删除好友
            
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Deleting friend %s", user_id)
        url = self._url + "/delete_friend"
        params = {
            'user_id': user_id
        }
        return self._make_request('POST', url, params=params)
        
    def delete_unidirectional_friend(self,user_id):
        """删除单向好友。
        
        参数:
            user_id (int): QQ号
            
        返回:
            bool: 是否成功删除单向好友
            
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Deleting unidirectional friend %s", user_id)
        url = self._url + "/delete_unidirectional_friend"
        params = {
            'user_id': user_id
        }
        return self._make_request('POST', url, params=params)
        
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
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Sending private message %s to user %s", message,user_id)
        url = self._url + "/send_private_msg"
        params = {
            'user_id': user_id,
            'message': message
        }
        for attempt in range(3):
            try:
                self.logger.debug("Attempt %s to send private message", attempt + 1)
                response = self._make_request('POST', url, params=params)
                return response
            except (requests.RequestException, QQBotAPIError):
                if attempt == 2:
                    raise
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
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Sending private message to user %s via get_group %s", user_id, group_id)
        url = self._url + "/send_private_msg"
        params = {
            'user_id': user_id,
            'message': message ,
            'group_id': group_id
        }
        for attempt in range(3):
            try:
                self.logger.debug("Attempt %s to send private message", attempt + 1)
                response = self._make_request('POST', url, params=params)
                return response
            except (requests.RequestException, QQBotAPIError):
                if attempt == 2:
                    raise
                time.sleep(1)
                continue
        
        raise QQBotAPIError("API request failed after 3 attempts", response)
    
    def send_group_message(self,message,group_id:int):
        """通过QQ机器人API向指定群组发送消息。

        参数:
            message (list): 要发送的消息内容
            group_id (int): 接收消息的QQ群号

        返回:dict
            message_id(int):消息 ID

        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Sending get_group message %s to get_group %s",message, group_id)
        url = self._url + "/send_group_msg"
        params = {
            'group_id': group_id,
            'message': message
        }
        return self._make_request('POST', url, params=params)

    def get_msg(self,message_id):
        """获取消息。
        
        参数:
            message_id (int): 消息ID
            
        返回:
            dict: 包含以下字段:
            - get_group (bool): 是否是群消息
            - group_id (int64): 群号(仅群消息)
            - message_id (int32): 消息id
            - real_id (int32): 消息真实id
            - message_type (str): 消息类型('get_group'或'private')
            - sender (dict): 发送者信息
                - nickname (str): 发送者昵称
                - user_id (int64): 发送者QQ号
            - time (int32): 发送时间
            - message (message): 消息内容
            - raw_message (message): 原始消息内容
            
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.debug("Getting message %s", message_id)
        url = self._url + "/get_msg"
        params = {
            'message_id': message_id
        }
        return self._make_request('POST', url, params=params)
        
    def delete_msg(self,message_id):
        """撤回消息。

        参数:
            message_id (int): 消息ID

        返回:
            bool: 是否成功删除消息

        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Deleting message %s", message_id)
        url = self._url + "/delete_msg"
        params = {
            'message_id': message_id
        }
        return self._make_request('POST', url, params=params)
        
    def mark_msg_as_read(self,message_id):
        """标记消息已读。

        参数:
            message_id (int): 消息ID

        返回:
            bool: 是否成功标记消息已读

        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Marking message %s as read", message_id)
        url = self._url + "/mark_msg_as_read"
        params = {
            'message_id': message_id
        }
        return self._make_request('POST', url, params=params)
        
    def get_forward_msg(self,message_id):
        """获取合并转发消息。
            
        参数:
            message_id (int): 消息ID
                
        返回:
            dict: 包含以下字段:
                - messages (list): 消息列表,每个元素包含:
                    - content (str): 消息内容
                    - sender (dict): 发送者信息
                        - nickname (str): 发送者昵称
                        - user_id (int): 发送者QQ号
                    - time (int): 发送时间
                
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.debug("Getting forward message %s", message_id)
        url = self._url + "/get_forward_msg"
        params = {
            'message_id': message_id
        }
        return self._make_request('POST', url, params=params)
        
    def send_group_forward_msg(self, group_id, messages):
        """发送群合并转发消息。

        参数:
            group_id (int): 群号
            messages (list): 自定义转发消息节点列表

        返回:
            dict: 包含以下字段:
                - message_id (int): 消息ID
                - forward_id (str): 转发消息ID

        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出 
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Sending get_group forward message to get_group %s", group_id)
        url = self._url + "/send_group_forward_msg"
        params = {
            'group_id': group_id,
            'messages': messages
        }
        return self._make_request('POST', url, params=params)
        
    def send_private_forward_msg(self,user_id,messages):
        """发送私聊合并转发消息。

        参数:
            user_id (int): 好友QQ号
            messages (list): 自定义转发消息节点列表

        返回:
            dict: 包含以下字段:
                - message_id (int): 消息ID
                - forward_id (str): 转发消息ID

        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Sending private forward message to user %s", user_id)
        url = self._url + "/send_private_forward_msg"
        params = {
            'user_id': user_id,
            'messages': messages
            }
        return self._make_request('POST', url, params=params)
        
    def get_group_msg_history(self,message_seq,group_id):
        """获取群消息历史记录。

        参数:
            message_seq (int64): 起始消息序号,可通过 get_msg 获得
            group_id (int64): 群号
            
        返回:
            dict: 包含以下字段:
                - messages (list): 从起始序号开始的前19条消息列表,每条消息格式见 Message
                
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.debug("Getting get_group message history")
        url = self._url + "/get_group_msg_history"
        params = {
            'message_seq': message_seq,
            'group_id': group_id
        }
        return self._make_request('POST', url, params=params)
    
    #图片
    def get_image(self,file):
        """获取图片信息。
        
        参数:
            file (str): 图片缓存文件名
            
        返回:
            dict: 包含以下字段:
            - size (int): 图片源文件大小
            - filename (str): 图片文件原名 
            - url (str): 图片下载地址
            
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.debug("Getting image %s", file)
        url = self._url + "/get_image"
        params = {
            'file': file
        }
        return self._make_request('POST', url, params=params)
        
    def ocr_image(self,image_id):
        """使用OCR识别图片中的文字。
        
        参数:
            image_id (str): 图片ID
                
        返回:
            dict: 包含以下字段:
                - texts (list): OCR识别结果,每个元素包含:
                    - text (str): 识别出的文本
                    - confidence (int): 置信度 
                    - coordinates (list): 文字坐标点列表
                - language (str): 识别出的语言
                
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.debug("Running OCR on image %s", image_id)
        url = self._url + "/ocr_image" 
        params = {
            'image': image_id
        }
        return self._make_request('POST', url, params=params)
    
    #语音
    def get_record(self,file,out_format):
        """获取语音文件。

        参数:
            file (str): 收到的语音文件名(消息段的file参数),如0B38145AA44505000B38145AA4450500.silk
            out_format (str): 要转换到的格式,支持mp3、amr、wma、m4a、spx、ogg、wav、flac

        返回:
            dict: 包含以下字段:
                - file (str): 转换后的语音文件路径

        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.debug("Getting audio file %s", file)
        url = self._url + "/get_record"
        params = {
            'file': file,
            'out_format': out_format
        }
        return self._make_request('POST', url, params=params)
        
    def can_send_record(self):
        """查询是否可以发送语音消息。
        
        返回:
            bool: 是否可以发送语音消息
            
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.debug("Checking if can send record")
        url = self._url + "/can_send_record"
        return self._make_request('POST', url)
    
    #文件
    def upload_group_file(self,group_id,file_path,file_name,folder):
        def upload_group_file(self,group_id,file_path,file_name,folder):
            """上传群文件。
            
            参数:
                group_id (int64): 群号
                file_path (str): 本地文件路径
                file_name (str): 储存名称
                folder (str): 父目录ID
                
            返回:
                bool: 上传是否成功
                
            异常:
                QQBotAPIError: 当API请求失败或返回非ok状态时抛出
                RequestException: 当网络请求失败时抛出
            """
            self.logger.info("Uploading file %s to get_group %s", file_name, group_id)
            url = self._url + "/upload_group_file"
            params = {
                'group_id': group_id,
                'file': file_path,
                'name': file_name,
                'folder': folder
            }
            return self._make_request('POST', url, params=params)
            
    def delete_group_file(self, group_id, file_id, busid):
        """删除群文件。

        参数:
            group_id (int64): 群号
            file_id (str): 文件ID
            busid (int): 文件类型

        返回:
            bool: 删除是否成功

        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Deleting file %s from get_group %s", file_id, group_id)
        url = self._url + "/delete_group_file"
        params = {
            'group_id': group_id,
            'file_id': file_id,
            'busid': busid
        }
        return self._make_request('POST', url, params=params)
    
    def create_group_file_folder(self, group_id, name, parent_id='/'):
        """创建群文件文件夹。
        
        参数:
            group_id (int): 群号
            name (str): 文件夹名称
            parent_id (str): 仅能为 '/'
            
        返回:
            bool: 是否创建成功
            
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Creating get_group folder %s in get_group %s", name, group_id)
        url = self._url + "/create_group_file_folder"
        params = {
            'group_id': group_id,
            'name': name,
            'parent_id': parent_id  
        }
        return self._make_request('POST', url, params=params)

    def delete_group_folder(self, group_id, folder_id):
        """删除群文件文件夹。
        
        参数:
            group_id (int): 群号
            folder_id (str): 文件夹ID
            
        返回:
            bool: 是否删除成功
            
        异常: 
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Deleting get_group folder %s from get_group %s", folder_id, group_id)
        url = self._url + "/delete_group_folder"
        params = {
            'group_id': group_id,
            'folder_id': folder_id
        }
        return self._make_request('POST', url, params=params)

    def get_group_file_system_info(self, group_id):
        """获取群文件系统信息。
        
        参数:
            group_id (int): 群号
            
        返回:
            dict: 包含以下字段:
                - file_count (int): 文件总数
                - limit_count (int): 文件上限  
                - used_space (int): 已使用空间
                - total_space (int): 空间上限
                
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.debug("Getting get_group file system info for get_group %s", group_id)
        url = self._url + "/get_group_file_system_info"
        params = {
            'group_id': group_id
        }
        return self._make_request('POST', url, params=params)

    def get_group_root_files(self, group_id):
        """获取群根目录文件列表。
        
        参数:
            group_id (int): 群号
            
        返回:
            dict: 包含以下字段:
                - files (list): 文件列表
                - folders (list): 文件夹列表
                
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.debug("Getting get_group root files for get_group %s", group_id)
        url = self._url + "/get_group_root_files"
        params = {
            'group_id': group_id
        }
        return self._make_request('POST', url, params=params)

    def get_group_files_by_folder(self, group_id, folder_id):
        """获取群子目录文件列表。
        
        参数:
            group_id (int): 群号
            folder_id (str): 文件夹ID
            
        返回:
            dict: 包含以下字段:
                - files (list): 文件列表  
                - folders (list): 文件夹列表
                
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.debug("Getting files in folder %s for get_group %s", folder_id, group_id)
        url = self._url + "/get_group_files_by_folder"
        params = {
            'group_id': group_id,
            'folder_id': folder_id
        }
        return self._make_request('POST', url, params=params)

    def get_group_file_url(self, group_id, file_id, busid):
        """获取群文件资源链接。
        
        参数:
            group_id (int): 群号
            file_id (str): 文件ID
            busid (int): 文件类型
            
        返回:
            str: 文件下载链接
            
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.debug("Getting download URL for file %s in get_group %s", file_id, group_id)
        url = self._url + "/get_group_file_url"
        params = {
            'group_id': group_id,
            'file_id': file_id,
            'busid': busid
        }
        return self._make_request('POST', url, params=params)

    def upload_private_file(self, user_id, file, name):
        """上传私聊文件。
        
        参数: 
            user_id (int): 对方QQ号
            file (str): 本地文件路径
            name (str): 文件名称
            
        返回:
            bool: 是否上传成功
            
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Uploading private file %s to user %s", file, user_id)
        url = self._url + "/upload_private_file"
        params = {
            'user_id': user_id,
            'file': file,
            'name': name
        }
        return self._make_request('POST', url, params=params)
    
    #处理请求
    def set_friend_add_request(self, flag, approve=True, remark=''):
        """处理加好友请求。
        
        参数:
            flag (str): 加好友请求的flag
            approve (bool): 是否同意请求
            remark (str): 添加后的好友备注
            
        返回:
            bool: 处理是否成功
            
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Processing friend request with flag: %s", flag)
        url = self._url + "/set_friend_add_request"
        params = {
            'flag': flag,
            'approve': approve,
            'remark': remark
        }
        return self._make_request('POST', url, params=params)

    def set_group_add_request(self, flag, sub_type, approve=True, reason=''):
        """处理加群请求/邀请。
        
        参数:
            flag (str): 加群请求的flag
            sub_type (str): 请求类型('add'或'invite')
            approve (bool): 是否同意
            reason (str): 拒绝理由
            
        返回:
            bool: 处理是否成功 
            
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Processing get_group request with flag: %s", flag)
        url = self._url + "/set_group_add_request" 
        params = {
            'flag': flag,
            'sub_type': sub_type,
            'approve': approve,
            'reason': reason
        }
        return self._make_request('POST', url, params=params)

    # 群信息
    def get_group_info(self, group_id, no_cache=False):
        """获取群信息。
        
        参数:
            group_id (int): 群号
            no_cache (bool): 是否不使用缓存
            
        返回:
            dict: 群信息包含:
                - group_id (int64): 群号
                - group_name (str): 群名称
                - group_memo (str): 群备注
                - group_create_time (int): 群创建时间
                - group_level (int): 群等级
                - member_count (int): 成员数
                - max_member_count (int): 最大成员数
                
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.debug("Getting info for get_group %s", group_id)
        url = self._url + "/get_group_info"
        params = {
            'group_id': group_id,
            'no_cache': no_cache
        }
        return self._make_request('POST', url, params=params)

    def get_group_list(self, no_cache=False):
        """获取群列表。
        
        参数:
            no_cache (bool): 是否不使用缓存
            
        返回:
            list: 群信息列表,每个元素格式同get_group_info的返回值
            
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.debug("Getting get_group list")
        url = self._url + "/get_group_list"
        params = {
            'no_cache': no_cache
        }
        return self._make_request('POST', url, params=params)

    def get_group_member_info(self,group_id,no_cache=False):
        """获取群成员信息。

        参数:
            group_id (int): 群号
            no_cache (bool): 是否不使用缓存(使用缓存可能更新不及时,但响应更快)

        返回:
            dict: 群成员信息

        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.debug("Getting member info for get_group %s", group_id)
        url = self._url + "/get_group_member_info"
        params = {
            'group_id': group_id,
            'no_cache': no_cache
        }
        return self._make_request('POST', url, params=params)

    def get_group_member_list(self, group_id, no_cache=False):
        """获取群成员列表。
        
        参数:
            group_id (int): 群号
            no_cache (bool): 是否不使用缓存
            
        返回:
            list: 群成员信息列表,每个元素格式同get_group_member_info的返回值
            
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.debug("Getting member list for get_group %s", group_id)
        url = self._url + "/get_group_member_list"
        params = {
            'group_id': group_id,
            'no_cache': no_cache
        }
        return self._make_request('POST', url, params=params)

    def get_group_honor_info(self, group_id, type='all'):
        """获取群荣誉信息。
        
        参数:
            group_id (int): 群号
            type (str): 要获取的群荣誉类型:
                - talkative: 龙王
                - performer: 群聊之火 
                - legend: 群聊炽焰
                - strong_newbie: 冒尖小春笋
                - emotion: 快乐之源
                - all: 获取所有数据
                
        返回:
            dict: 群荣誉信息,包含:
                - group_id: 群号
                - current_talkative: 当前龙王信息(type为talkative或all时)
                - talkative_list: 历史龙王列表 
                - performer_list: 群聊之火列表
                - legend_list: 群聊炽焰列表
                - strong_newbie_list: 冒尖小春笋列表
                - emotion_list: 快乐之源列表
                
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.debug(f"Getting honor info for get_group {group_id}, type {type}")
        url = self._url + "/get_group_honor_info"
        params = {
            'group_id': group_id,
            'type': type
        }
        return self._make_request('POST', url, params=params)

    def get_group_system_msg(self):
        """获取群系统消息。
        
        返回:
            dict: 包含以下字段:
                - invited_requests: 邀请消息列表
                - join_requests: 进群消息列表
                
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.debug("Getting get_group system messages")
        url = self._url + "/get_group_system_msg"
        return self._make_request('POST', url)

    def get_essence_msg_list(self, group_id):
        """获取精华消息列表。
        
        参数:
            group_id (int): 群号
            
        返回:
            list: 精华消息列表,每个元素包含:
                - sender_id: 发送者QQ号
                - sender_nick: 发送者昵称
                - sender_time: 消息发送时间
                - operator_id: 操作者QQ号 
                - operator_nick: 操作者昵称
                - operator_time: 设置精华时间
                - message_id: 消息ID
                
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.debug(f"Getting essence messages for get_group {group_id}")
        url = self._url + "/get_essence_msg_list"
        params = {'group_id': group_id}
        return self._make_request('POST', url, params=params)

    def get_group_at_all_remain(self, group_id):
        """获取群 @全体成员 剩余次数。
        
        参数:
            group_id (int): 群号
            
        返回:
            dict: 包含以下字段:
                - can_at_all: 是否可以@全体成员
                - remain_at_all_count_for_group: 群内所有管理当天剩余@全体成员次数
                - remain_at_all_count_for_uin: Bot当天剩余@全体成员次数
                
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.debug(f"Getting @all remaining count for get_group {group_id}")
        url = self._url + "/get_group_at_all_remain"
        params = {'group_id': group_id}
        return self._make_request('POST', url, params=params)

    # 群设置
    def set_group_name(self, group_id, group_name):
        """设置群名。
        
        参数:
            group_id (int): 群号
            group_name (str): 新群名
            
        返回:
            bool: 是否设置成功
            
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Setting name for get_group %s to %s", group_id, group_name)
        url = self._url + "/set_group_name"
        params = {
            'group_id': group_id,
            'group_name': group_name
        }
        return self._make_request('POST', url, params=params)

    def set_group_admin(self, group_id, user_id, enable=True):
        """设置群管理员。
        
        参数:
            group_id (int): 群号
            user_id (int): 要设置管理的QQ号
            enable (bool): 是否设为管理
            
        返回:
            bool: 是否设置成功
            
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Setting admin status for user %s in get_group %s: %s",
                      user_id, group_id, "enable" if enable else "disable")
        url = self._url + "/set_group_admin"
        params = {
            'group_id': group_id,
            'user_id': user_id,
            'enable': enable
        }
        return self._make_request('POST', url, params=params)

    def set_group_portrait(self, group_id, file, cache=1):
        """设置群头像。
        
        参数:
            group_id (int): 群号
            file (str): 图片文件路径或URL或Base64编码
            cache (int): 是否使用缓存,默认1
                
        返回:
            bool: 是否设置成功
                
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Setting portrait for get_group %s", group_id)
        url = self._url + "/set_group_portrait"
        params = {
            'group_id': group_id,
            'file': file,
            'cache': cache
        }
        return self._make_request('POST', url, params=params)

    def set_group_card(self, group_id, user_id, card=''):
        """设置群名片(群备注)。
        
        参数:
            group_id (int): 群号
            user_id (int): 要设置的QQ号
            card (str): 群名片内容,不填或空字符串表示删除群名片
                
        返回:
            bool: 是否设置成功
                
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Setting card for user %s in get_group %s", user_id, group_id)
        url = self._url + "/set_group_card"
        params = {
            'group_id': group_id,
            'user_id': user_id,
            'card': card
        }
        return self._make_request('POST', url, params=params)

    def set_group_special_title(self, group_id, user_id, special_title='', duration=-1):
        """设置群组专属头衔。
        
        参数:
            group_id (int): 群号
            user_id (int): 要设置的QQ号 
            special_title (str): 专属头衔,不填或空字符串表示删除专属头衔
            duration (int): 显示专属头衔的有效期,秒,-1表示永久
                
        返回:
            bool: 是否设置成功
                
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Setting special title for user %s in get_group %s", user_id, group_id)
        url = self._url + "/set_group_special_title" 
        params = {
            'group_id': group_id,
            'user_id': user_id,
            'special_title': special_title,
            'duration': duration
        }
        return self._make_request('POST', url, params=params)

    # 群操作
    def set_group_ban(self, group_id, user_id, duration=1800):
        """群单人禁言。
        
        参数:
            group_id (int): 群号
            user_id (int): 要禁言的QQ号
            duration (int): 禁言时长(秒),0表示取消禁言
                
        返回:
            bool: 是否禁言成功
                
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Setting ban for user %s in get_group %s for %s seconds",
                    user_id, group_id, duration)
        url = self._url + "/set_group_ban"
        params = {
            'group_id': group_id,
            'user_id': user_id, 
            'duration': duration
        }
        return self._make_request('POST', url, params=params)

    def set_group_whole_ban(self, group_id, user_id, duration=1800):
        """群成员单人禁言。
        
        参数:
            group_id (int): 群号
            user_id (int): 要禁言的QQ号
            duration (int): 禁言时长，单位秒，0表示取消禁言，默认1800秒
            
        返回:
            bool: 是否设置成功
            
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Setting ban for user %s in get_group %s for %s seconds",
                      user_id, group_id, duration)
        url = self._url + "/set_group_ban"
        params = {
            'group_id': group_id,
            'user_id': user_id,
            'duration': duration
        }
        return self._make_request('POST', url, params=params)

    def set_group_anonymous_ban(self, group_id, anonymous=None, anonymous_flag=None, duration=1800):
        """群匿名用户禁言。
        
        参数:
            group_id (int): 群号
            anonymous (dict): 要禁言的匿名对象(群消息上报的anonymous字段)
            anonymous_flag (str): 要禁言的匿名用户flag(从群消息获得) 
            duration (int): 禁言时长(秒)
            
        返回:
            bool: 是否禁言成功
            
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Setting anonymous ban in get_group %s for %s seconds",
                        group_id, duration)
        url = self._url + "/set_group_anonymous_ban"
        params = {
            'group_id': group_id,
            'duration': duration 
        }
        if anonymous:
            params['anonymous'] = anonymous
        if anonymous_flag:
            params['anonymous_flag'] = anonymous_flag

        return self._make_request('POST', url, params=params)

    def set_group_kick(self, group_id, user_id, reject_add_request=False):
        """群组踢人。
        
        参数:
            group_id (int): 群号
            user_id (int): 要踢的QQ号
            reject_add_request (bool): 是否拒绝此人后续加群请求
                
        返回:
            bool: 是否成功踢出
                
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Kicking user %s from get_group %s", user_id, group_id)
        url = self._url + "/set_group_kick"
        params = {
            'group_id': group_id,
            'user_id': user_id,
            'reject_add_request': reject_add_request
        }
        return self._make_request('POST', url, params=params)

    def set_group_leave(self, group_id, is_dismiss=False):
        """退出群组。
        
        参数:
            group_id (int): 群号
            is_dismiss (bool): 是否解散群(仅群主可用)
                
        返回:
            bool: 退出是否成功
                
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出 
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Leaving get_group %s, dismiss: %s", group_id, is_dismiss)
        url = self._url + "/set_group_leave"
        params = {
            'group_id': group_id,
            'is_dismiss': is_dismiss
        }
        return self._make_request('POST', url, params=params)
        
        def set_group_whole_ban(self, group_id, enable=True):
            """群全员禁言。
            
            参数:
                group_id (int): 群号
                enable (bool): 是否开启全员禁言
                    
            返回:
                bool: 操作是否成功
                    
            异常:
                QQBotAPIError: 当API请求失败或返回非ok状态时抛出
                RequestException: 当网络请求失败时抛出
            """
            self.logger.info("Setting whole get_group ban for get_group %s: %s",
                            group_id, "enable" if enable else "disable")
            url = self._url + "/set_group_whole_ban"
            params = {
                'group_id': group_id,
                'enable': enable
            }
            return self._make_request('POST', url, params=params)
    
    def set_group_anonymous(self, group_id, enable=True):
        """群匿名聊天。
        
        参数:
            group_id (int): 群号
            enable (bool): 是否允许匿名聊天
                
        返回:
            bool: 操作是否成功
                
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Setting anonymous chat for get_group %s: %s",
                        group_id, "enable" if enable else "disable")
        url = self._url + "/set_group_anonymous"
        params = {
            'group_id': group_id,
            'enable': enable
        }
        return self._make_request('POST', url, params=params)
    
    def set_group_essence_msg(self, message_id):
        """设置群精华消息。
        
        参数:
            message_id (int): 消息ID
                
        返回:
            bool: 操作是否成功
                
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Setting essence message %s", message_id)
        url = self._url + "/set_essence_msg"
        params = {'message_id': message_id}
        return self._make_request('POST', url, params=params)
    
    def delete_group_essence_msg(self, message_id):
        """移出群精华消息。
        
        参数:
            message_id (int): 消息ID
                
        返回:
            bool: 操作是否成功
                
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Deleting essence message %s", message_id)
        url = self._url + "/delete_essence_msg"
        params = {'message_id': message_id}
        return self._make_request('POST', url, params=params)
    
    def send_group_sign(self, group_id):
        """群打卡。
        
        参数:
            group_id (int): 群号
                
        返回:
            bool: 操作是否成功
                
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Sending get_group sign for get_group %s", group_id)
        url = self._url + "/send_group_sign"
        params = {'group_id': group_id}
        return self._make_request('POST', url, params=params)
    
    def set_group_anonymous_ban(self, group_id, anonymous_flag=None, anonymous=None, duration=1800):
        """群匿名用户禁言。
        
        参数:
            group_id (int): 群号
            anonymous_flag (str): 匿名用户的flag
            anonymous (dict): 匿名用户的信息
            duration (int): 禁言时长，单位秒，0 表示取消禁言
                
        返回:
            bool: 操作是否成功
                
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Setting anonymous ban in get_group %s", group_id)
        url = self._url + "/set_group_anonymous_ban"
        params = {
            'group_id': group_id,
            'duration': duration
        }
        if anonymous_flag:
            params['anonymous_flag'] = anonymous_flag
        if anonymous:
            params['anonymous'] = anonymous
        return self._make_request('POST', url, params=params)
    
    def send_group_notice(self, group_id, content, image=None):
        """发送群公告。
        
        参数:
            group_id (int): 群号
            content (str): 公告内容
            image (str, optional): 图片路径
            
        返回:
            bool: 是否发送成功
            
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.info("Sending get_group notice to get_group %s", group_id)
        url = self._url + "/send_group_notice"
        params = {
            'group_id': group_id,
            'content': content
        }
        if image:
            params['image'] = image
            
        return self._make_request('POST', url, params=params)
        
    def get_group_notice(self, group_id):
        """获取群公告。
        
        参数:
            group_id (int): 群号
            
        返回:
            list: 公告列表，每个元素包含：
                - sender_id (int): 公告发表者QQ号
                - publish_time (int): 公告发表时间戳
                - message (dict): 公告内容
                    - text (str): 公告文本内容
                    - images (list): 公告图片列表
                        - height (str): 图片高度 
                        - width (str): 图片宽度
                        - id (str): 图片ID
                    
        异常:
            QQBotAPIError: 当API请求失败或返回非ok状态时抛出
            RequestException: 当网络请求失败时抛出
        """
        self.logger.debug("Getting notices for get_group %s", group_id)
        url = self._url + "/get_group_notice"
        params = {'group_id': group_id}
        return self._make_request('POST', url, params=params)

    # 扩展API
    def set_qq_avatar(self, file: str) -> dict:
        """设置QQ头像
            
        参数:
            file (str): 头像文件路径，支持 http://, file://, base64://
            
        返回:
            dict: API响应数据
        """
        url = self._url + "/set_qq_avatar"
        data = {'file': file}
        return self._make_request('POST', url, json=data)
    
    def get_group_ignore_add_request(self) -> list:
        """获取已过滤的加群通知
        
        返回:
            list: 包含被过滤的加群请求信息
        """
        url = self._url + "/get_group_ignore_add_request"
        return self._make_request('POST', url)
    
    def get_file(self, file_id: str, base64: bool = False) -> dict:
        """下载收到的群文件或私聊文件
        
        参数:
            file_id (str): 文件ID
            base64 (bool): 是否返回base64编码的文件内容
            
        返回:
            dict: 包含文件信息的字典
        """
        url = self._url + "/get_file"
        data = {
            'file_id': file_id,
            'base64': base64
        }
        return self._make_request('POST', url, json=data)
    
    def forward_friend_single_msg(self, user_id: int, message_id: int) -> dict:
        """转发单条消息给好友
        
        参数:
            user_id (int): 目标好友QQ号
            message_id (int): 要转发的消息ID
        """
        url = self._url + "/forward_friend_single_msg"
        data = {
            'user_id': user_id,
            'message_id': message_id
        }
        return self._make_request('POST', url, json=data)
    
    def forward_group_single_msg(self, group_id: int, message_id: int) -> dict:
        """转发单条消息到群
        
        参数:
            group_id (int): 目标群号
            message_id (int): 要转发的消息ID
        """
        url = self._url + "/forward_group_single_msg"
        data = {
            'group_id': group_id,
            'message_id': message_id
        }
        return self._make_request('POST', url, json=data)
    
    def set_msg_emoji_like(self, message_id: str, emoji_id: str) -> dict:
        """发送表情回应
        
        参数:
            message_id (str): 消息ID
            emoji_id (str): 表情ID
        """
        url = self._url + "/set_msg_emoji_like"
        data = {
            'message_id': message_id,
            'emoji_id': emoji_id
        }
        return self._make_request('POST', url, json=data)
    
    def get_friends_with_category(self) -> list:
        """获取带分组信息的好友列表
        
        返回:
            list: 好友分组信息列表
        """
        url = self._url + "/get_friends_with_category"
        return self._make_request('POST', url)
    
    def set_online_status(self, status: int, ext_status: int = 0, battery_status: int = 0) -> dict:
        """设置在线状态
        
        参数:
            status (int): 在线状态码(10:在线 30:离开 40:隐身 50:忙碌 60:Q我吧 70:请勿打扰)
            ext_status (int): 扩展状态
            battery_status (int): 电池状态
        """
        url = self._url + "/set_online_status"
        data = {
            'status': status,
            'ext_status': ext_status,
            'battery_status': battery_status
        }
        return self._make_request('POST', url, json=data)
    
    def get_profile_like(self) -> dict:
        """获取自身点赞列表"""
        url = self._url + "/get_profile_like"
        return self._make_request('POST', url)
    
    def friend_poke(self, user_id: int) -> dict:
        """好友戳一戳
        
        参数:
            user_id (int): 好友QQ号
        """
        url = self._url + "/friend_poke"
        data = {'user_id': user_id}
        return self._make_request('POST', url, json=data)
    
    def group_poke(self, group_id: int, user_id: int) -> dict:
        """群组戳一戳
        
        参数:
            group_id (int): 群号
            user_id (int): 要戳的成员QQ号
        """
        url = self._url + "/group_poke"
        data = {
            'group_id': group_id,
            'user_id': user_id
        }
        return self._make_request('POST', url, json=data)