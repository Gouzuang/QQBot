from fastapi import FastAPI, Request
import logging
import os
from datetime import datetime

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

logger = logging.getLogger(__name__)

@app.post("/")
async def submit(request: Request):
    try:
        data = await request.json()
        logger.debug(f"Received data: {data}")
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")

# 运行应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)