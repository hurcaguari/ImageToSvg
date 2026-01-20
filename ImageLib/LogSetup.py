import logging
import colorlog

def setup_logging(level: int = logging.INFO) -> None:
    """
    配置日志系统
    
    :param level: 日志级别，默认为 INFO
    """
    formatter = colorlog.ColoredFormatter(
        fmt='%(log_color)s%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
            'GITHUB': 'blue'
        }
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    
    # 避免重复添加handler
    if not root.handlers:
        root.addHandler(handler)