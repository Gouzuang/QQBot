from datetime import datetime
import json
import sys
import traceback

import yaml
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

def setup_log_directory():
        """设置日志目录和全局日志文件路径"""
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file_path = os.path.join(log_dir, f'app_{timestamp}.log')
        
        # 配置根日志记录器
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        file_handler.setFormatter(formatter)
        
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        
        logging.basicConfig(
            level=logging.DEBUG,
            handlers=[file_handler, stream_handler]
        )
# 初始化日志配置
setup_log_directory()
logger = logging.getLogger(__name__)

# 创建实例
app = FastAPI()

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

def load_config():
    try:
        config_path = os.path.join(os.getcwd(), 'AppData', 'config.yaml')
        with open(config_path, 'r') as config_file:
            logger.info(f"Read Configuration file in {config_path}")
            return yaml.safe_load(config_file)
    except FileNotFoundError:
        logger.error(f"Configuration file not found in {config_path}, creating a default one.")
        default_config = {
            'bot': {
                'host': 'http://localhost:3000'
            }
        }
        with open(config_path, 'w') as config_file:
            yaml.safe_dump(default_config, config_file)
        return default_config

config = load_config()
bot = QQBotAPI.QQBot(config['bot']['host'])

# Initialize function list
message_functions = []
quiet_functions = []
extern_call_functions = []
regular_task_functions = []
# Import all modules from apps directory
for _, name, _ in pkgutil.iter_modules(['apps']):
    module = importlib.import_module(f'apps.{name}')
    for function in module.functions:
        if function.register()['type'] == 'message_function':
            message_functions.append(function)
        elif function.register()[type] == 'quiet_function':
            quiet_functions.append(function)
        elif function.register()['type'] == 'regular_task_function':
            regular_task_functions.append(function)
        elif function.register()['type'] == 'extern_call_function':
            extern_call_functions.append(function)
            app.add_api_route(f"/extern_call/{function['name']}", function['function'], methods=["POST"])

@app.post("/message")
async def submit(request: Request):
    try:
        message = await request.json()
        logger.debug(f"Received data: \n {json.dumps(message, indent=4, ensure_ascii=False)}")
        
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
            
    # 正常的消息处理流程
    logger.info(f"检测是否需要Resolver: {message_chain.get_message_id()}")
    resolver = None
    if message_chain.is_group:
        for msg in message_chain.message:
            if isinstance(msg, AtMessage) and msg == bot.qq_id:
                resolver = Resolver(message_chain, bot, message_functions,is_quiet_function=False)
                break
        if resolver == None:
            logger.info(f"Message {message_chain.get_message_id()} is not for me {bot.qq_id} in group, finding quiet functions")
            resolver = Resolver(message_chain, bot, quiet_functions, is_quiet_function=True)
    else:
        resolver = Resolver(message_chain, bot, message_functions, is_quiet_function=False)
        

    

# 运行应用
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000,reload_dirs=["./apps"])