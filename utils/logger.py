import logging
import sys

def setup_logger(name: str = "DeliverySystem", level: int = logging.INFO) -> logging.Logger:
    """
    Sets up a logger with standard formatting and stream handler.
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if not logger.handlers:
        logger.setLevel(level)
        handler = logging.StreamHandler(sys.stdout)
        
        # Format: [Timestamp] [Level] [LoggerName] - Message
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger
