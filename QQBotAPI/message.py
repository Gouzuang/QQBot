from functools import lru_cache
from .data import QQ_FACE_DISCRIPTION 
from .person import Person

class MessageChain():
    def __init__(self):
        pass
        
    def format_message(self,msg):
        if msg["type"] == "Text":
            return TextMessage(msg["data"]["text"])
        elif msg["type"] == "Image":
            return ImageMessage(msg["data"]["url"], msg["data"]["name"], msg["data"]["file_size"])
        elif msg["type"] == "Face":
            return BuildInFaceMessage(msg["data"]["face_id"])
        elif msg["type"] == "At":
            return AtMessage(msg["data"]["target"])
        elif msg["type"] == "File":
            return FileMessage(msg["data"]["url"], msg["data"]["name"], msg["data"]["file_size"], msg["data"]["file_id"], msg["data"]["path"])
        elif msg["type"] == "Voice":
            return VoiceMessage(msg["data"]["url"], msg["data"]["file_name"], msg["data"]["file_size"], msg["data"]["path"])
        elif msg["type"] == "Json":
            return JsonMessage(msg["data"]["json"])
        
    
class ReceivedMessageChain(MessageChain):
    def __init__(self,raw_data):
        self._raw_data = raw_data
        self._self_id = raw_data["self_id"]
        self._time = raw_data["time"]
        self._message_type = raw_data["message_type"]
        self._message_id = raw_data["message_id"]
        self._message_seq = raw_data["message_seq"]
        
        self._sender = Person(raw_data["sender"]["user_id"], raw_data["sender"]["nickname"], raw_data["sender"]["card"])
        
        self._message = []
        for msg in raw_data["message"]:
            self._message.append(self.format_message(msg))
            
    def sender(self):
        return self._sender
        
    def __str__(self):
        str = f"{self._sender}:\n"
        for msg in self._message:
            str += f"{msg}"
        return str
    
    def reply(self,message):
        """回复消息"""
        return SentMessageChain.reply_to(self)
    
class SentMessageChain(MessageChain):
    def __init__(self):
        self._message = []
        
    def add_message(self,message):
        if isinstance(message, ReplyFlag):
            if any(isinstance(msg, ReplyFlag) for msg in self._message):
                raise ValueError("Cannot add multiple ReplyFlag messages in single message")
        self._message.append(message)
        
    def json(self):
        messages = []
        for msg in self._message:
            messages.append(msg.json())
        return messages
    
    @classmethod
    def convert_from_received(cls, received_message):
        """将ReceivedMessageChain的消息内容复制给SentMessageChain"""
        sent_message = cls()
        for msg in received_message._message:
            sent_message.add_message(msg)
        return sent_message
    
    @classmethod
    def reply_to(cls, received_message):
        """创建一个回复消息"""
        sent_message = cls()
        sent_message.add_message(ReplyFlag(received_message))
        return sent_message

class ReplyFlag():
    def __init__(self,message):
        if isinstance(message, int):
            self._message_id = message
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
        return {
            "reply": self._message_id
        }

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
        self._target = target
        
    def __str__(self):
        return self._target
    
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