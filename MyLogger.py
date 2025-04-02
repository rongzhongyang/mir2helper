import os
import logging
import logging.handlers
from logging.handlers import RotatingFileHandler
class MyLogger:
    def __init__(self, log_dir='logs', log_name='vccdaddy', max_log_size=10 * 1024 * 1024, backup_count=5,
                 log_level=100):
        self.log_dir = log_dir
        self.log_name = log_name + '.log'
        self.max_log_size = max_log_size
        self.backup_count = backup_count

        # 创建日志目录
        os.makedirs(self.log_dir, exist_ok=True)

        # 创建RotatingFileHandler，实现日志文件自动切割
        log_file = os.path.join(self.log_dir, self.log_name)
        handler = RotatingFileHandler(log_file, maxBytes=max_log_size, backupCount=backup_count, encoding='utf-8')
        # formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        formatter = logging.Formatter('%(asctime)s %(message)s')
        handler.setFormatter(formatter)

        # 创建Logger对象
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(log_level)
        self.logger.addHandler(handler)

    def log(self, message, log_level=100):
        self.logger.log(log_level, message)