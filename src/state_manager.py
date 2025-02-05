import time
from typing import Callable, Dict, Any

class StateManager:
    def __init__(self):
        self._waiting_states: Dict[str, Dict[str, Any]] = {}
        
    def add_waiting_state(self, 
                         response_id: str, 
                         error_id: str, 
                         callback: Callable, 
                         timeout: int = 300,
                         data: Any = None) -> None:
        """添加一个等待状态"""
        self._waiting_states[f"{response_id}:{error_id}"] = {
            "callback": callback,
            "expire_time": time.time() + timeout,
            "data": data
        }
    
    def get_callback(self, response_id: str, error_id: str) -> tuple[Callable, Any] | None:
        """获取回调函数和相关数据"""
        key = f"{response_id}:{error_id}"
        if key in self._waiting_states:
            state = self._waiting_states[key]
            if time.time() < state["expire_time"]:
                return state["callback"], state["data"]
            else:
                del self._waiting_states[key]
        return None
        
    def remove_state(self, response_id: str, error_id: str) -> None:
        """移除等待状态"""
        key = f"{response_id}:{error_id}"
        if key in self._waiting_states:
            del self._waiting_states[key]
