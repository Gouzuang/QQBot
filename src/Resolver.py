import logging
from logging.handlers import RotatingFileHandler
import os
import uuid

from QQBotAPI.message import *


class Resolver:
    """每个消息传入都会生成Resolver，用于响应消息"""
    def __init__(self, message, QQBot, functions, state_manager):
        self.message = message
        self.QQBot = QQBot
        self.logger = self._setup_logger()
        self.functions = functions
        #创建全局唯一的 响应ID
        self.response_id = str(uuid.uuid4())
        self.state_manager = state_manager
        
    def _setup_logger(self):
        """为每个Resolver实例设置独立的日志记录器"""
        logger = logging.getLogger(f'Main.Resolver.{self.response_id}')
        
        # 设置日志格式
        formatter = logging.Formatter('%(asctime)s - Resolver - %(response_id)s - %(levelname)s - %(message)s',
                                   defaults={'response_id': self.response_id})
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 文件处理器
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'qqbot_error.log'),
            maxBytes=1024*1024,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        logger.setLevel(logging.ERROR)
        logger.propagate = False
        
        return logger

    def _find_function(self):
        """查找对应的函数"""
        response_function = []
        for function in self.functions:
            if function['type'] == 'message_function':
                res = function.check(self.message)
                if res != "":
                    self.logger.info(f"Found function: {function['name']} in condition: {res}")
                    response_function.append(function)
                    
        if len(response_function) == 0:
            self.logger.info("No function found")
        elif len(response_function) == 1:
            self.logger.info(f"Function {response_function[0]['name']} selected")
            return response_function[0](self.message, self.QQBot)
        elif len(response_function) > 1:
            self.logger.info("Multiple functions found. Asking for user input")
            error_id = "0x0001"
            sent_message = self.message.reply_chain()
            sent_message.message.extend([
                TextMessage("响应ID: " + self.response_id),
                TextMessage("Error ID:" + error_id),
                TextMessage("发现多个符合条件的功能：")
            ])
            
            for i, func in enumerate(response_function):
                sent_message.message.append(TextMessage(f"{i+1}. {func['name']}"))
            
            sent_message.message.append(TextMessage("回复此消息以选择功能，5分钟有效"))
            sent_message.send()
            
            # 注册等待状态
            self.state_manager.add_waiting_state(
                self.response_id,
                error_id,
                self._find_function_response,
                timeout=300,
                data=response_function
            )

    def _find_function_response(self, message, functions):
        """处理用户的选择"""
        try:
            select = int(message.text)
            if 0 < select <= len(functions):
                self.logger.info(f"User selected function {functions[select-1]['name']}")
                return functions[select-1](self.message, self.QQBot)
            else:
                self.logger.error(f"Invalid selection: {select}")
                self.message.reply("无效的选择")
        except ValueError as e:
            self.logger.error(f"Error processing user selection: {str(e)}")
            self.message.reply("选择格式错误")
        finally:
            self.state_manager.remove_state(self.response_id, "0x0001")