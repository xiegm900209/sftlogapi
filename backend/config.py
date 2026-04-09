import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    LOG_DIR = os.environ.get('LOG_DIR') or '../testlogs/testlogs'
    INDEX_DIR = os.environ.get('INDEX_DIR') or '../logs_index'
    CONFIG_DIR = os.environ.get('CONFIG_DIR') or '../config'

    # 允许的文件扩展名
    ALLOWED_EXTENSIONS = {'.log', '.txt'}