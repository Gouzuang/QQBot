from abc import ABC, abstractmethod
from typing import Optional
from QQBotAPI import QQBot
from QQBotAPI.message import MessageChain, ReceivedMessageChain


class FunctionTemplate(ABC):
    """Base template class for bot functions"""

    @abstractmethod
    def __init__(self,msg:ReceivedMessageChain,bot:QQBot):
        """Initialize function instance"""
        pass

    @classmethod
    @abstractmethod
    def check(cls, message: MessageChain) -> str:
        """
        Check if message matches function criteria
        Args:
            message: MessageChain to check
        Returns:
            str: Matched rule or empty string if no match
        """
        pass

    @classmethod
    @abstractmethod
    def register(cls) -> tuple[str, str]:
        """
        Register function name and type
        Returns:
            tuple[str, str]: (function_name, function_type)
        """
        pass

    @abstractmethod
    def process(self):
        """
        Process message
        """
        pass

    def get_route_table(self) -> Optional[dict]:
        """
        Get routing table for extern_call_function type
        Returns:
            Optional[dict]: Route table if type is extern_call_function, None otherwise
        """
        pass