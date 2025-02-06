from functools import lru_cache
from typing import Union
from .data import QQ_FACE_DISCRIPTION 
from .person import Person, Group

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
            return FileMessage(msg["data"]["url"], msg["data"]["name"], msg["data"]["file_size"], msg["data"]["file_id"], msg["data"]["path"])
        elif msg["type"] == "voice":
            return VoiceMessage(msg["data"]["url"], msg["data"]["file_name"], msg["data"]["file_size"], msg["data"]["path"])
        elif msg["type"] == "json":
            return JsonMessage(msg["data"]["json"])
        elif msg["type"] == "reply":
            self.is_reply = True
            self.reply_info = int(msg["data"]["id"])
            return ReplyFlag(msg["data"]["id"])
        
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
            
    def sender(self):
        return self._sender
    
    def get_message_id(self):
        return self._message_id
    
    def time(self):
        return self._time
    
    def message_id(self):
        return self._message_id
    
    def group(self):
        if self.is_group:
            return self._group
        else:
            return None
        
    def __str__(self):
        str = f"{self._sender}:\n"
        for msg in self.message:
            str += f"{msg}"
        return str
    
    def json(self):
        return self._raw_data
    
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
        
    def json(self):
        messages = []
        for msg in self.message:
            messages.append(msg.json())
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
        
    def json(self):
        return {'type': 'reply', 'data': {'id': self._message_id}}

class TextMessage():
    def __init__(self, text):
        self._text = text
        
    def __str__(self):
        return self._text
    
    def json(self):
        return {
            "type": "text",
            "data": {
                "text": self._text
            }
        }
    
class ImageMessage():
    def __init__(self, url,name,file_size):
        self._url = url
        self._name = name
        self._file_size = file_size
        
    def __str__(self):
        return self._name
    
    def json(self):
        return {
            "type": "image",
            "data": {
                "url": self._url,
                "name": self._name,
                "file_size": self._file_size
            }
        }
    
class BuildInFaceMessage():
    def __init__(self, face_id):
        self._face_id = int(face_id)
        self._description = self.find_description(self._face_id)
    
    def find_description(self, face_id):
        return QQ_FACE_DISCRIPTION.get(face_id, "无描述")
        
    def __str__(self):
        return f"[表情:{self._description}]"
    
class AtMessage():
    def __init__(self, target):
        self.target = target
        
    def __str__(self):
        return self.target
    
    def __eq__(self, value):
        return self.target == value

    def json(self):
        return {
            "type": "at",
            "data": {
                "qq": self.target
            }
        }
    
class FileMessage():
    def __init__(self, url,name,file_size,file_id,path):
        self._url = url
        self._name = name
        self._file_size = file_size
        self._file_id = file_id
        self._path = path
        
    def __str__(self):
        return self._name
    
class VoiceMessage():
    def __init__(self, url,file_name,file_size,path):
        self._url = url
        self._file_name = file_name
        self._file_size = file_size
        self._path = path
        
    def __str__(self):
        return self._file_name
    
class JsonMessage():
    def __init__(self, json):
        self._json = json
        
    def __str__(self):
        return self._json