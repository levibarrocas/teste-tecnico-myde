import logging
import json
import sys
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

def setup_logging():
    json_handler = logging.StreamHandler(sys.stdout)
    json_handler.setFormatter(JSONFormatter())
    
    # Intercept common loggers and force them to use our JSON handler
    for logger_name in ("", "uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        logger.handlers = [json_handler]
        logger.propagate = False
