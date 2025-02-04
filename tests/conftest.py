import pytest
import logging

@pytest.fixture(autouse=True)
def disable_logging():
    """禁用测试期间的日志输出"""
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)
