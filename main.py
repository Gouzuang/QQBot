from fastapi import FastAPI, Request
import logging
import os
from datetime import datetime

# Ensure the log directory exists
os.makedirs("log", exist_ok=True)
# Generate a timestamp for the log file name
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file_path = f"log/app_{timestamp}.log"

logging.basicConfig(level=logging.DEBUG, handlers=[logging.FileHandler(log_file_path), logging.StreamHandler()])
# 创建FastAPI应用
app = FastAPI()

# 配置日志记录
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.post("/")
async def submit(request: Request):
    # 获取请求体
    data = await request.json()
    # 记录日志
    logger.debug(f"Received data: {data}")

# 运行应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)