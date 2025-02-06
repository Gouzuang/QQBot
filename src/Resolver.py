import logging
from logging.handlers import RotatingFileHandler
import os
import traceback
from typing import Callable, List
import uuid
from QQBotAPI.errors import QQBotAPIError
from QQBotAPI.message import *


class Resolver:
    """每个消息传入都会生成Resolver，用于响应消息"""
    def __init__(self, message:Union[MessageChain,ReceivedMessageChain], QQBot, functions:List[Callable]):
        self.message = message
        self.QQBot = QQBot
        self.functions = functions
        #创建全局唯一的 响应ID
        self.response_id = str(uuid.uuid4())
        self.logger = logging.getLogger(__name__+" - "+self.response_id)

        
        self.logger.info(f"New Resolver created with response ID: {self.response_id}")
        try:
            self.function = self._find_function()
            if self.function == "Multiple functions found":
                pass
            elif self.function == "No function found":
                pass
            else:
                self.logger.info(f"Function returned: {self.function}")
                self.function(message,QQBot)
        except (ConnectionError, QQBotAPIError) as e:
            self.logger.error(f"Error processing message: {str(e)}")
            raise e
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            self.logger.error(traceback.format_exc())
            if not isinstance(e, (ConnectionError, QQBotAPIError)):
                if isinstance(message, ReceivedMessageChain):
                    self.message.reply("发生错误: " + str(e),QQBot)
    

    def _find_function(self):
        """查找对应的函数"""
        response_function = []
        for function in self.functions:
            if function.register()['type'] == 'message_function':
                res = function.check(self.message)
                if res != "":
                    self.logger.info(f"Found function: {function.register()['name']} in condition: {res}")
                    response_function.append(function)
                    
        if len(response_function) == 0:
            self.logger.info("No function found")
            return "No function found"
        elif len(response_function) == 1:
            self.logger.info(f"Function {response_function[0].register()['name']} selected")
            return response_function[0]
        elif len(response_function) > 1:
            self.logger.info("Multiple functions found. Asking for user input")
            error_id = "0x0001"
            sent_message = self.message.reply_chain()
            sent_message.message.extend([
                TextMessage("响应ID: " + self.response_id),
                TextMessage("发现多个符合条件的功能：")
            ])