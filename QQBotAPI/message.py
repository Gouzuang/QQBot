from functools import lru_cache
import json
from typing import Union
from .data import QQ_FACE_DISCRIPTION 
from .person import Person, Group
import os
import requests
from .config import CachePath
class MessageChain():
    def __init__(self):
        pass
        
    def format_message(self,msg):
        if msg["type"] == "text":
            return TextMessage(msg["data"]["text"])
        elif msg["type"] == "image":
            return ImageMessage(msg["data"]["url"], msg["data"]["file"], msg["data"]["file_size"])
        elif msg["type"] == "face":
            return BuildInFaceMessage(msg["data"]["id"])
        elif msg["type"] == "at":
            return AtMessage(msg["data"]["qq"])
        elif msg["type"] == "file":
            return FileMessage(msg["data"]["url"], msg["data"]["file"], msg["data"]["file_size"], msg["data"]["file_id"], msg["data"]["path"])
        elif msg["type"] == "voice":
            return VoiceMessage(msg["data"]["url"], msg["data"]["file_name"], msg["data"]["file_size"], msg["data"]["path"])
        elif msg["type"] == "json":
            return JsonMessage(msg["data"])
        elif msg["type"] == "reply":
            self.is_reply = True
            self.reply_info = int(msg["data"]["id"])
            return ReplyFlag(msg["data"]["id"])
        
    def format_message_from_db(self,msg):
        if msg["type"] == "text":
            return TextMessage.json_from_db(msg)
        elif msg["type"] == "image":
            return ImageMessage.json_from_db(msg)
        elif msg["type"] == "face":
            return BuildInFaceMessage(msg["data"]["id"])
        elif msg["type"] == "at":
            return AtMessage.json_from_db(msg)
        elif msg["type"] == "file":
            return FileMessage.json_from_db(msg)
        elif msg["type"] == "voice":
            return VoiceMessage.json_from_db(msg)
        elif msg["type"] == "json":
            return JsonMessage.json_from_db(msg)
        elif msg["type"] == "reply":
            self.is_reply = True
            self.reply_info = int(msg["data"]["id"])
            return ReplyFlag.json_from_db(msg)
        
class ReceivedMessageChain(MessageChain):
    def __init__(self,raw_data):
        self._raw_data = raw_data
        self._self_id = raw_data["self_id"]
        self._time = raw_data["time"]
        self._message_type = raw_data["message_type"]
        self._message_id = raw_data["message_id"]
        self._message_seq = raw_data["message_seq"]
        if "group_id" in raw_data:
            self._group = Group(raw_data["group_id"])
            self.is_group = True
        else:
            self._group = None
            self.is_group = False
        self.is_reply = False
        
        self._sender = Person(raw_data["sender"]["user_id"], raw_data["sender"]["nickname"], raw_data["sender"]["card"])
        
        self.message = []
        for msg in raw_data["message"]:
            self.message.append(self.format_message(msg))
            
    def get_sender(self):
        return self._sender
    
    def get_message_id(self):
        return self._message_id
    
    def get_time(self):
        return self._time
    
    def get_message_id(self):
        return self._message_id
    
    def get_group(self) -> Group:
        if self.is_group:
            return self._group
        else:
            return None
        
    def __str__(self):
        str = f"{self._sender}:\n"
        for msg in self.message:
            str += f"{msg}"
        return str
    
    def get_json(self) -> dict:
        return json.dumps(self._raw_data)
    
    def get_json_for_db(self) -> dict:
        return {
            "self_id": self._self_id,
            "time": self._time,
            "message_type": self._message_type,
            "message_id": self._message_id,
            "message_seq": self._message_seq,
            "group_id": self._group.get_group_id() if self.is_group else None,
            "sender": self._sender.get_json(),
            "message": [msg.get_json_for_db() for msg in self.message]
        }
    
    @classmethod
    def json_from_db(self,json:Union[dict,str]):
        if isinstance(json, str):
            json = json.loads(json)
        ret = ReceivedMessageChain(json)
        ret.message = [ret.format_message_from_db(msg) for msg in json["message"]]
        return ret
    
    def text_only(self):
        return "".join([str(msg) for msg in self.message if isinstance(msg, TextMessage)])
    
    def reply_chain(self,message):
        """回复消息"""
        return ReplyMessageChain(self)
    
    def reply(self,message:Union[MessageChain,str,list],qqbot):
        """回复消息"""
        reply_chain = self.reply_chain(message)
        if isinstance(message, str):
            reply_chain.add_message(TextMessage(message))
        elif isinstance(message, list):
            reply_chain.message.extend(message)
        else:
            reply_chain.message.extend(message.message)
        reply_chain.send(qqbot)
        
    def convert_to_sent(self):
        return SentMessageChain.convert_from_received(self)
    
class SentMessageChain(MessageChain):
    def __init__(self):
        self.message = []
        
    def add_message(self,message):
        if isinstance(message, ReplyFlag):
            if any(isinstance(msg, ReplyFlag) for msg in self.message):
                raise ValueError("Cannot add multiple ReplyFlag messages in single message")
        self.message.append(message)
        
    def get_json(self) -> dict:
        messages = []
        for msg in self.message:
            messages.append(msg.get_json())
        return messages
    
    @classmethod
    def convert_from_received(cls, received_message):
        """将ReceivedMessageChain的消息内容复制给SentMessageChain"""
        sent_message = cls()
        for msg in received_message.message:
            sent_message.add_message(msg)
        return sent_message
    
class ReplyMessageChain(SentMessageChain):
    def __init__(self, reply_message:MessageChain):
        self.message = []
        self.message.append(ReplyFlag(reply_message))
        if reply_message.is_group:
            self._is_group = True
            self._group = reply_message._group
        else:
            self._is_group = False
            self._group = None
        self._sender = reply_message._sender
        
    def send(self,qqbot):
        if self._is_group:
            qqbot.send_group_message(self._group, self.message)
        else:
            qqbot.send_private_message(self._sender, self.message)

class ReplyFlag():
    def __init__(self,message:Union[str,int,MessageChain]):
        if isinstance(message, int):
            self._message_id = message
            self._raw_data = None
        elif isinstance(message, str):
            self._message_id = int(message)
            self._raw_data = None
        elif isinstance(message, MessageChain):
            self._message_id = message._message_id
            self._raw_data = MessageChain
        else:
            raise TypeError("message must be int or MessageChain")
        
    def __str__(self):
        if self._raw_data:
            return f"Reply to {self._raw_data} sent by {self._raw_data.sender()}:"
        
    def get_json(self):
        return {'type': 'reply', 'data': {'id': self._message_id}}

    def get_json_for_db(self):
        return {'type': 'reply', 'data': {'id': self._message_id}}
    
    @classmethod
    def json_from_db(self,json:Union[dict,str]):
        if isinstance(json, str):
            json = json.loads(json)
        data = json.get("data")
        return ReplyFlag(data.get("id"))
    
class TextMessage():
    def __init__(self, text):
        self._text = text
        
    def __str__(self):
        return str(self._text)  # 确保返回字符串类型
    
    def get_json(self):
        return {
            "type": "text",
            "data": {
                "text": self._text
            }
        }
    
    def get_json_for_db(self):
        return {
            "type": "text",
            "data": {
                "text": self._text
            }
        }
    
    @classmethod
    def json_from_db(self,json:Union[dict,str]):
        if isinstance(json, str):
            json = json.loads(json)
        data = json.get("data")
        return TextMessage(data.get("text"))
    
class ImageMessage():
    def __init__(self, url,name,file_size):
        self._url = url
        self._name = name
        self._file_size = file_size
        self._is_downloaded = False
        self._path = None
        
    def __str__(self):
        return self.name
    
    def get_json(self):
        return {
            "type": "image",
            "data": {
                "url": self._url,
                "file": self._name,
                "file_size": self._file_size
            }
        }
        
    def get_json_for_db(self):
        return {
            "type": "image",
            "data": {
                "url": self._url,
                "file": self._name,
                "file_size": self._file_size,
            },
            "bot": {
                "path": self._path
            }
        }
        
    @classmethod
    def json_from_db(self,json:Union[dict,str]):
        if isinstance(json, str):
            json = json.loads(json)
        data = json.get("data")
        message = ImageMessage(data.get("url"), data.get("file"), data.get("file_size"))
        data = json.get("bot")
        message._path = data.get("path")
        message._is_downloaded = True
        return message
         
    def download(self):
        file_path = os.path.join(CachePath.image_path(), self._name)
        
        response = requests.get(self._url)
        response.raise_for_status()
        
        with open(file_path, 'wb') as f:
            f.write(response.content)
            
        return file_path
   
class BuildInFaceMessage():
    def __init__(self, face_id):
        self._face_id = int(face_id)
        self._description = self.find_description(self._face_id)
    
    def find_description(self, face_id):
        return QQ_FACE_DISCRIPTION.get(face_id, "无描述")
        
    def __str__(self):
        return f"[表情:{self._description}]"
    
    def get_json(self):
        return {
            "type": "face",
            "data": {
                "id": self._face_id
            }
        }
    
    def get_json_for_db(self):
        return {
            "type": "face",
            "data": {
                "id": self._face_id
            }
        }
        
class AtMessage():
    def __init__(self, target:Union[str,int,Person]):
        if isinstance(target, Person):
            self._target = target.user_id()
        elif isinstance(target, str):
            self._target = target
        elif isinstance(target, int):
            self._target = target
        
    def __str__(self):
        return self._target
    
    def __eq__(self, value:Union[str,int,Person]):
        if isinstance(value, Person):
            return self._target == value.user_id()
        elif isinstance(value, str):
            return self._target == value
        elif isinstance(value, int):
            return self._target == str(value)

    def get_json(self):
        return {
            "type": "at",
            "data": {
                "qq": self._target
            }
        }
    
    def get_target(self):
        return self._target
    
    def get_json_for_db(self):
        return {
            "type": "at",
            "data": {
                "qq": self._target
            }
        }
    
    @classmethod
    def json_from_db(self,json:Union[dict,str]):
        if isinstance(json, str):
            json = json.loads(json)
        data = json.get("data")
        return AtMessage(data.get("qq"))

class FileMessage():
    def __init__(self, url,name,file_size,file_id,path):
        self._url = url
        self._name = name
        self._file_size = file_size
        self._file_id = file_id
        self._path = path
        
    def __str__(self):
        return self._name
    
    def get_url(self):
        return self._url
    def get_name(self):
        return self._name
    def get_file_size(self):
        return self._file_size
    def get_file_id(self):
        return self._file_id
    def get_path(self):
        return self._path
    
    def get_json(self):
        return {
            "type": "file",
            "data": {
                "url": self._url,
                "file": self._name,
                "file_size": self._file_size,
                "file_id": self._file_id,
                "path": self._path
            }
        }
    
    def get_json_for_db(self):
        return {
            "type": "file",
            "data": {
                "url": self._url,
                "file": self._name,
                "file_size": self._file_size,
                "file_id": self._file_id,
                "path":self._path
            },
            "bot": {
                "path": self._path
            }
        }
    
    @classmethod
    def json_from_db(self,json:Union[dict,str]):
        if isinstance(json, str):
            json = json.loads(json)
        data = json.get("data")
        message = FileMessage(data.get("url"), data.get("file"), data.get("file_size"), data.get("file_id"),data.get("path"))
        data = json.get("bot")
        message._path = data.get("path")
        return message
      
class VoiceMessage():
    def __init__(self, url, file_name, file_size, path=None):  # 添加path的默认值
        self._url = url
        self._file_name = file_name
        self._file_size = file_size
        self._path = path
        self._is_downloaded = path is not None
        
    def __str__(self):
        return self._file_name
    
    def get_url(self):
        return self._url
    def get_file_name(self):
        return self._file_name
    def get_file_size(self):
        return self._file_size
    def get_path(self):
        return self._path
    
    def get_json(self):
        return {
            "type": "voice",
            "data": {
                "url": self._url,
                "file_name": self._file_name,
                "file_size": self._file_size,
                "path": self._path
            }
        }
    
    def get_json_for_db(self):
        return {
            "type": "voice",
            "data": {
                "url": self._url,
                "file_name": self._file_name,
                "file_size": self._file_size
            },
            "bot": {
                "path": self._path
            }
        }
        
    @classmethod
    def json_from_db(self,json:Union[dict,str]):
        if isinstance(json, str):
            json = json.loads(json)
        data = json.get("data")
        message = VoiceMessage(data.get("url"), data.get("file_name"), data.get("file_size"))
        data = json.get("bot")
        message._path = data.get("path")
        return message
        
class JsonMessage():
    def __init__(self, json):
        self._json = json
        
    def __str__(self):
        return self._json
    
    def get_json(self):
        return {
            "type": "json",
            "data": self._json
        }
        
    def get_json_for_db(self):
        return {
            "type": "json",
            "data": self._json
        }
        
    @classmethod
    def json_from_db(self,json:Union[dict,str]):
        if isinstance(json, str):
            json = json.loads(json)
        data = json.get("data")
        return JsonMessage(data)

