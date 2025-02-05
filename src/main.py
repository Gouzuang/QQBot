import sys
from fastapi import FastAPI, Request
import logging
import os
from datetime import datetime
import uvicorn
import importlib
import pkgutil
from Resolver import Resolver
from state_manager import StateManager

# Ensure the log directory exists
os.makedirs("logs", exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file_path = f"logs/app_{timestamp}.log"

# 配置日志处理器，明确指定UTF-8编码
file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
stream_handler = logging.StreamHandler()

# 创建格式化器
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# 配置根日志记录器
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[file_handler, stream_handler]
)

# 创建FastAPI应用
app = FastAPI()
state_manager = StateManager()
logger = logging.getLogger(__name__)

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
        
        # 检查是否是对等待状态的响应
        if hasattr(message, 'reply_id') and hasattr(message, 'error_id'):
            callback_data = state_manager.get_callback(message.reply_id, message.error_id)
            if callback_data:
                callback, data = callback_data
                return callback(message, data)
        
        # 正常的消息处理流程
        resolver = Resolver(message, bot, functions, state_manager)
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")

# 运行应用
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000,reload_dirs=["./apps"])