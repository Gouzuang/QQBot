import time
from typing import Callable, Dict, Any, Union
import sqlalchemy
from QQBotAPI.person import Group, Person
from shared.log import LogConfig
from QQBotAPI.message import MessageChain, ReceivedMessageChain

class StateManager:
    def __init__(self):
        self._waiting_states: Dict[str, Dict[str, Any]] = {}
        
    def add_waiting_state(self, 
                         message_id: int,
                         callback: Callable, 
                         timeout: int = 300,
                         data: Any = None) -> None:
        """添加一个等待状态"""
        self._waiting_states[f"{message_id}"] = {
            "callback": callback,
            "expire_time": time.time() + timeout,
            "data": data
        }
    
    def get_callback(self, reply_message_id:Union[int,str,MessageChain]) -> tuple[Callable, Any] | None:
        """获取回调函数和相关数据"""
        if isinstance(reply_message_id, MessageChain):
            reply_message_id = reply_message_id.message_id
        elif isinstance(reply_message_id, str):
            reply_message_id = int(reply_message_id)
        elif isinstance(reply_message_id, int):
            key = f"{reply_message_id}"
        
        if key in self._waiting_states:
            state = self._waiting_states[key]
            if time.time() < state["expire_time"]:
                return state["callback"], state["data"]
            else:
                del self._waiting_states[key]
        return None
        
    def remove_state(self, message_id) -> None:
        """移除等待状态"""
        key = f"{message_id}"
        if key in self._waiting_states:
            del self._waiting_states[key]

