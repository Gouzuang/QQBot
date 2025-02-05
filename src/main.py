import sys
import traceback
from fastapi import FastAPI, Request
import logging
import os
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse
import uvicorn
import importlib
import pkgutil
from QQBotAPI.message import *
import QQBotAPI
from Resolver import Resolver
from manager import StateManager
from shared.log import LogConfig

# 初始化日志配置
log_config = LogConfig()
logger = log_config.get_logger(__name__)

# 创建实例
app = FastAPI()
state_manager = StateManager()
bot = QQBotAPI.QQBot("192.168.3.100:3000",1)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)
# Initialize function list
message_functions = []
extern_call_functions = []
regular_task_functions = []
# Import all modules from apps directory
for _, name, _ in pkgutil.iter_modules(['apps']):
    module = importlib.import_module(f'apps.{name}')
    for function in module.functions:
        if function.register()['type'] == 'message_function':
            message_functions.append(function)
        elif function.register()['type'] == 'regular_task_function':
            regular_task_functions.append(function)
        elif function.register()['type'] == 'extern_call_function':
            extern_call_functions.append(function)
            app.add_api_route(f"/extern_call/{function['name']}", function['function'], methods=["POST"])

@app.post("/message")
async def submit(request: Request):
    try:
        message = await request.json()
        logger.debug(f"Received data: {message}")
        
        if message["post_type"] == "meta_event":
            if message["meta_event_type"] == "heartbeat":
                pass
        
        elif message["post_type"] == "message":
            process_message(message)
                
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        logger.error(traceback.format_exc())

def process_message(message):
    message_chain = ReceivedMessageChain(message)
    bot.MessageManager.add_message(message_chain)
    # 检查是否是对等待状态的响应
    try:
        if message_chain.is_reply:
            callback_data = state_manager.get_callback(message_chain.reply_info)
            if callback_data:
                logger.info(f"message is a reply for a Resolver: {message}")
                callback, data = callback_data
                callback(message, data)
                return
    except Exception as e:
        logger.info(f"message is not a reply for a Resolver: {message}")
            
    # 正常的消息处理流程
    if message_chain.is_group:
        for msg in message_chain.message:
            if isinstance(msg, AtMessage) and msg.target == bot.qq_id:
                resolver = Resolver(message_chain, bot, message_functions, state_manager)
                break
    else:
        resolver = Resolver(message_chain, bot, message_functions, state_manager)

# 运行应用
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000,reload_dirs=["./apps"])