import sys
import json
import logging
from loguru import logger

def serialize(record):
    """Serialize log record to structured JSON format."""
    subset = {
        "timestamp": record["time"].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["module"],
        "function": record["function"],
        "line": record["line"],
        "extra": record["extra"]
    }
    return json.dumps(subset)

def json_sink(message):
    serialized = serialize(message.record)
    print(serialized, file=sys.stdout, flush=True)

class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

def configure_logger(log_level: str = "INFO"):
    """Configure Loguru to emit JSON logs and intercept standard library logging."""
    logger.remove()
    logger.add(json_sink, level=log_level)
    
    # Intercept standard library logs (FastAPI, uvicorn, etc.)
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    for _log in ["uvicorn", "uvicorn.error", "fastapi", "chromadb"]:
        _logger = logging.getLogger(_log)
        _logger.handlers = [InterceptHandler()]

__all__ = ["configure_logger", "logger"]
