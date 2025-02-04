import pytest
from QQBotAPI.message import Person, MessageChain, TextMessage, ImageMessage, BuildInFaceMessage, AtMessage, FileMessage, VoiceMessage, JsonMessage

def test_person():
    person = Person(123456, "测试昵称", "群名片")
    assert person.user_id() == 123456
    assert person.nickname() == "测试昵称"
    assert person.card() == "群名片"
    assert str(person) == "测试昵称(群名片)"

    person_no_card = Person(123456, "测试昵称")
    assert str(person_no_card) == "测试昵称"

def test_message_types():
    text_msg = TextMessage("Hello World")
    assert str(text_msg) == "Hello World"

    image_msg = ImageMessage("http://example.com/image.jpg", "test.jpg", 1024)
    assert str(image_msg) == "test.jpg"

    face_msg = BuildInFaceMessage("10")
    assert str(face_msg) == "[表情:尴尬]"
    
    face_msg = BuildInFaceMessage(24)
    assert str(face_msg) == "[表情:饥饿]"

    at_msg = AtMessage("@用户名")
    assert str(at_msg) == "@用户名"

def test_message_chain():
    raw_data = {
        "self_id": 123456,
        "time": 1677649230,
        "message_type": "group",
        "message_id": 1234,
        "message_seq": 5678,
        "sender": {
            "user_id": 987654,
            "nickname": "发送者",
            "card": "群名片"
        },
        "message": [
            {"type": "Text", "data": {"text": "你好，"}},
            {"type": "At", "data": {"target": "@某人"}},
            {"type": "Text", "data": {"text": "！"}}
        ]
    }
    
    msg_chain = MessageChain(raw_data)
    assert msg_chain._self_id == 123456
    assert msg_chain._message_type == "group"
    assert str(msg_chain._sender) == "发送者(群名片)"
    assert len(msg_chain._message) == 3
    assert str(msg_chain).startswith("发送者(群名片):\n")

def test_complex_messages():
    file_msg = FileMessage("http://example.com/file.zip", "test.zip", 2048, "file123", "/path/to/file")
    assert str(file_msg) == "test.zip"

    voice_msg = VoiceMessage("http://example.com/voice.mp3", "voice.mp3", 1024, "/path/to/voice")
    assert str(voice_msg) == "voice.mp3"

    json_msg = JsonMessage('{"key": "value"}')
    assert str(json_msg) == '{"key": "value"}'
