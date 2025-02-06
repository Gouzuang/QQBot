import pytest
from QQBotAPI.QQBotHttp import QQBotHttp
from unittest.mock import patch, Mock
import requests
from QQBotAPI.errors import QQBotAPIError

@pytest.fixture
def qq_bot():
    return QQBotHttp("http://test.url", client_id=123456)

@patch('requests.post')
def test_make_request_post_success(mock_post, qq_bot):
    mock_response = Mock()
    mock_response.json.return_value = {
        'status': 'ok',
        'data': {'test': 'data'}
    }
    mock_post.return_value = mock_response
    
    result = qq_bot._make_request('POST', 'http://test.url/test', {'param': 'test'})
    
    assert result == {'test': 'data'}
    mock_post.assert_called_once_with('http://test.url/test', json={'param': 'test'})

@patch('requests.get')  
def test_make_request_get_success(mock_get, qq_bot):
    mock_response = Mock()
    mock_response.json.return_value = {
        'status': 'ok',
        'data': {'test': 'data'}
    }
    mock_get.return_value = mock_response
    
    result = qq_bot._make_request('GET', 'http://test.url/test', {'param': 'test'})
    
    assert result == {'test': 'data'}
    mock_get.assert_called_once_with('http://test.url/test', params={'param': 'test'})

@patch('requests.post')
def test_make_request_error(mock_post, qq_bot):
    mock_response = Mock()
    mock_response.json.return_value = {
        'status': 'failed',
        'message': 'error'
    }
    mock_post.return_value = mock_response
    
    with pytest.raises(QQBotAPIError):
        qq_bot._make_request('POST', 'http://test.url/test', {'param': 'test'})

@patch('requests.post')
def test_get_login_info(mock_post, qq_bot):
    mock_response = Mock()
    mock_response.json.return_value = {
        'status': 'ok',
        'data': {
            'user_id': 123456,
            'nickname': 'test_bot'
        }
    }
    mock_post.return_value = mock_response
    
    result = qq_bot.get_login_info()
    
    assert result == {
        'user_id': 123456,
        'nickname': 'test_bot'
    }
    mock_post.assert_called_once()

@patch('requests.post')
def test_send_private_message(mock_post, qq_bot):
    mock_response = Mock()
    mock_response.json.return_value = {
        'status': 'ok',
        'data': {
            'message_id': 123
        }
    }
    mock_post.return_value = mock_response
    
    result = qq_bot.send_private_message("test message", 123456)
    
    assert result == {'message_id': 123}
    mock_post.assert_called_once()

@patch('requests.post')
def test_send_group_message(mock_post, qq_bot):
    mock_response = Mock()
    mock_response.json.return_value = {
        'status': 'ok',
        'data': {
            'message_id': 123
        }
    }
    mock_post.return_value = mock_response
    
    result = qq_bot.send_group_message("test message", 123456)
    
    assert result == {'message_id': 123}
    mock_post.assert_called_once()

@patch('requests.post')
def test_get_stranger_info(mock_post, qq_bot):
    mock_response = Mock()
    mock_response.json.return_value = {
        'status': 'ok',
        'data': {
            'user_id': 123456,
            'nickname': 'test_user',
            'sex': 'unknown',
            'age': 0
        }
    }
    mock_post.return_value = mock_response
    
    result = qq_bot.get_stranger_info(123456)
    
    assert result == {
        'user_id': 123456,
        'nickname': 'test_user',
        'sex': 'unknown',
        'age': 0
    }
    mock_post.assert_called_once()

@patch('requests.get')
def test_get_friend_list(mock_get, qq_bot):
    mock_response = Mock()
    mock_response.json.return_value = {
        'status': 'ok',
        'data': [
            {
                'user_id': 123456,
                'nickname': 'friend1',
                'remark': 'test_friend'
            }
        ]
    }
    mock_get.return_value = mock_response
    
    result = qq_bot.get_friend_list()
    
    assert result == [
        {
            'user_id': 123456,
            'nickname': 'friend1',
            'remark': 'test_friend'
        }
    ]
    mock_get.assert_called_once()