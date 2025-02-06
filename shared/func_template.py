from abc import ABC, abstractmethod
from typing import Optional
from QQBotAPI.message import MessageChain

class FunctionTemplate(ABC):
    """Base template class for bot functions"""
    
    def __init__(self):
        """Initialize function instance"""
        self.name = self.register()[0]
        self.type = self.register()[1]

    @abstractmethod
    def check(self, message: MessageChain) -> str:
        """
        Check if message matches function criteria
        Args:
            message: MessageChain to check
        Returns:
            str: Matched rule or empty string if no match
        """
        pass

    @abstractmethod
    def register(self) -> tuple[str, str]:
        """
        Register function name and type
        Returns:
            tuple[str, str]: (function_name, function_type)
        """
        pass

    def get_route_table(self) -> Optional[dict]:
        """
        Get routing table for extern_call_function type
        Returns:
            Optional[dict]: Route table if type is extern_call_function, None otherwise
        """
        if self.type == "extern_call_function":
            return {}
        return None