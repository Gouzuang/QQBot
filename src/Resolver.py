import logging
from logging.handlers import RotatingFileHandler
import os
import traceback
from typing import Callable, List, Type
import uuid
from QQBotAPI.errors import QQBotAPIError
from QQBotAPI.message import *
from src.func_template import FunctionTemplate


class MultipleFunctionFoundError():
    pass
class NoFunctionFoundError():
    pass

class Resolver:
    """每个消息传入都会生成Resolver，用于响应消息"""
    def __init__(self, message:Union[MessageChain,ReceivedMessageChain], QQBot, functions:List[FunctionTemplate], is_quiet_function = False):
        self.message = message
        self.QQBot = QQBot
        self.functions = functions
        #创建全局唯一的 响应ID
        self.response_id = str(uuid.uuid4())
        self.logger = logging.getLogger(__name__+" - "+self.response_id)
        self.is_quiet_function = is_quiet_function
        
        self.logger.info(f"New Resolver created with response ID: {self.response_id}")
        try:
            self.function = self._find_function()
            self._use_function(self.function)
        except (ConnectionError, QQBotAPIError) as e:
            self.logger.error(f"Error processing message: {str(e)}")
            raise e
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            self.logger.error(traceback.format_exc())
            if not isinstance(e, (ConnectionError, QQBotAPIError)):
                if isinstance(message, ReceivedMessageChain) and not self.is_quiet_function:
                    self.message.reply("发生错误: " + str(e),QQBot)

    def _use_function(self, function:List[Type[FunctionTemplate]]):
        if len(function) == 0:
            self.logger.info("No function found")
            sent_message = self.message.reply_chain()
            sent_message.message.extend([
                TextMessage("响应ID: " + self.response_id),
                TextMessage("未找到符合条件的功能")
            ])
        elif len(function) == 1:
            self.logger.info(f"Function {function[0].register()['name']} selected")
            function[0](self.message, self.QQBot).process()
        elif len(function) > 1:
            if self.is_quiet_function:
                self.logger.info("Multiple functions found, but is quiet function")
                for f in function:
                    try:
                        self.logger.info(f"Function {f.register()['name']} Running")
                        f(self.message, self.QQBot).process()
                    except Exception as e:
                        self.logger.error(f"Error processing message: {str(e)}")
                        self.logger.error(traceback.format_exc())
            else:
                sent_message = self.message.reply_chain()
                sent_message.message.extend([
                    TextMessage("响应ID: " + self.response_id),
                    TextMessage("发现多个符合条件的功能：")
                ])


    def _find_function(self) -> callable:
        """查找对应的函数"""
        response_function = []
        for function in self.functions:
            res = function.check(self.message)
            if res != "" and res != False and res != None:
                self.logger.info(f"Found function: {function.register()['name']} in condition: {res}")
                response_function.append(function)
        return response_function
