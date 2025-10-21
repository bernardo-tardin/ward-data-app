import os
import logging
from logging.handlers import TimedRotatingFileHandler

def setup_logger(name, log_to_file=False, log_level=logging.INFO, backup_count=7):
    """
    Configures and returns a logger with the specified name and log rotation.

    If a logger with the same name has already been configured, the existing
    instance is returned without modification to avoid duplicate handlers.

    Log rotation is daily ('D') and keeps a history defined by `backup_count`.
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if logger is already configured
    if logger.hasHandlers():
        return logger

    logger.setLevel(log_level)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    if log_to_file:
        log_dir = os.environ.get('LOG_DIR', './logs') 
        
        try:
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f'{name}.log')
            
            file_handler = TimedRotatingFileHandler(
                log_file, 
                when="D", 
                interval=1, 
                backupCount=backup_count,
                encoding='utf-8' 
            )

            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
        except (PermissionError, IOError) as e:
            # Notify that the log file could not be created
            logging.warning(f"Could not write log file to {log_dir}: {e}. Logs will be sent to console only.")
            # Ensure logs still appear in the console on failure
            if not logger.handlers:
                 console_handler = logging.StreamHandler()
                 console_handler.setFormatter(formatter)
                 logger.addHandler(console_handler)

    # If log_to_file is False, or if it failed, add a console handler
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger