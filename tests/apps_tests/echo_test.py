import pytest
from unittest.mock import Mock, patch
from apps.echo import echo_message
from QQBotAPI.message import ReceivedMessageChain, TextMessage
from QQBotAPI.errors import DataNotFoundInDataBaseError
from QQBotAPI.person import Person, Group

def create_test_message(text="test message", message_id=123, is_group=False):
    """Helper to create test message data"""
    msg_data = {
        "self_id": 10000,
        "time": 1600000000,
        "message_type": "group" if is_group else "private",
        "message_id": message_id,
        "message_seq": 1,
        "sender": {
            "user_id": 20000,
            "nickname": "Test User",
            "card": ""
        },
        "message": [
            {
                "type": "text",
                "data": {
                    "text": text
                }
            }
        ]
    }
    
    if is_group:
        msg_data["group_id"] = 30000
        
    return msg_data

@pytest.mark.asyncio
async def test_echo_message_success():
    # Mock QQBot instance
    mock_bot = Mock()
    mock_message_manager = Mock()
    mock_bot.MessageManager = mock_message_manager
    
    # Create source message that we'll echo
    source_msg_data = create_test_message("Original message", 100)
    source_msg = ReceivedMessageChain(source_msg_data)
    
    # Create reply message containing "echo" command
    reply_msg_data = create_test_message("echo", 200)
    reply_msg = ReceivedMessageChain(reply_msg_data)
    reply_msg.is_reply = True
    reply_msg.reply_info = 100
    
    # Setup MessageManager mock to return source message
    mock_message_manager.get_message_via_id.return_value = source_msg
    
    # Test echo functionality 
    echo = echo_message(reply_msg, mock_bot)
    
    # Verify message lookup was called correctly
    mock_message_manager.get_message_via_id.assert_called_once_with(100, reply_msg.get_group())
    
    # Verify reply was sent with original message
    reply_msg.reply.assert_called_once_with(source_msg, mock_bot)

def test_echo_check_valid():
    # Create message with "echo" text and reply flag
    msg_data = create_test_message("echo")
    msg = ReceivedMessageChain(msg_data)
    msg.is_reply = True
    
    result = echo_message.check(msg)
    assert result == "echo"

def test_echo_check_invalid():
    # Test cases that should not trigger echo
    test_cases = [
        # No reply flag
        {"text": "echo", "is_reply": False},
        # Wrong text
        {"text": "not echo", "is_reply": True},
        # Empty text
        {"text": "", "is_reply": True}
    ]
    
    for case in test_cases:
        msg_data = create_test_message(case["text"])
        msg = ReceivedMessageChain(msg_data)
        msg.is_reply = case["is_reply"]
        
        result = echo_message.check(msg)
        assert result == ""

def test_register():
    reg_info = echo_message.register()
    assert reg_info["type"] == "message_function"
    assert reg_info["name"] == "echo_message"