
class Person():
    def __init__(self, user_id, nickname='',card=''):
        self._user_id = user_id
        self._nickname = nickname
        self._card = card
        
    def user_id(self):
        return self._user_id
    def nickname(self):
        return self._nickname
    def card(self):
        return self._card
    
    def __str__(self):
        str = ""
        str += f"{self.nickname()}"
        if self._card != "":
            str += f"({self.card()})"
        return str

class MessageChain():
    def __init__(self, raw_data):
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
        
    
    def format_message(self,msg):
        if msg["type"] == "Text":
            return TextMessage(msg["data"]["text"])
        elif msg["type"] == "Image":
            return ImageMessage(msg["data"]["url"], msg["data"]["name"], msg["data"]["file_size"])
        elif msg["type"] == "Face":
            return FaceMessage(msg["data"]["face_id"])
        elif msg["type"] == "At":
            return AtMessage(msg["data"]["target"])
        elif msg["type"] == "File":
            return FileMessage(msg["data"]["url"], msg["data"]["name"], msg["data"]["file_size"], msg["data"]["file_id"], msg["data"]["path"])
        elif msg["type"] == "Voice":
            return VoiceMessage(msg["data"]["url"], msg["data"]["file_name"], msg["data"]["file_size"], msg["data"]["path"])
        elif msg["type"] == "Json":
            return JsonMessage(msg["data"]["json"])
        
    def __str__(self):
        str = f"{self._sender}:\n"
        for msg in self._message:
            str += f"{msg}"
        return str
        
        
class TextMessage():
    def __init__(self, text):
        self._text = text
        
    def __str__(self):
        return self._text
    
class ImageMessage():
    def __init__(self, url,name,file_size):
        self._url = url
        self._name = name
        self._file_size = file_size
        
    def __str__(self):
        return self._name
    
class FaceMessage():
    def __init__(self, face_id):
        self._face_id = face_id
        
    def __str__(self):
        return self._face_id
    
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