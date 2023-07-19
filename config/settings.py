import datetime
import logging
import multiprocessing
import os
import re
from pathlib import Path
from dotenv import load_dotenv
import logging.config as log_conf

load_dotenv()

# --- GENERAL
NUMBER_OF_AVAILABLE_CPU_CORES = multiprocessing.cpu_count() + 2
CURRENT_DATE = datetime.datetime.today().strftime("%Y%m%d")

# DB / REDIS
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_DB = os.getenv("REDIS_DB")
REDIS_HOST = os.getenv("REDIS_HOST")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_BROKER_BACKEND = os.getenv("CELERY_BROKER_BACKEND")

# --- DIRECTORIES
BASE_DIR = Path(__file__).resolve().parent.parent
WORDLISTS_DIR = f"{BASE_DIR}/utils/wordlists"
LOGGING_DIR = f"{BASE_DIR}/logs/"
TESTS_MOCKED_INPUT_DIR = f"{BASE_DIR}/tests/mocked_user_input"

# --- MODULES
# STEERING_MODULE
STEERING_MODULE = "steering_module"

# TASK_QUEUE
TASK_QUEUE = "task_queue"

# REQUEST_MANAGER
REQUEST_MANAGER = "request_manager"

# DIRECTORY_BRUTEFORCE
DIRECTORY_BRUTEFORCE = "directory_bruteforce"
DIRECTORY_BRUTEFORCE_REQUEST_METHOD = "GET"

CORE_MODULES = [STEERING_MODULE, TASK_QUEUE, REQUEST_MANAGER]
RECON_PHASE_MODULES = [DIRECTORY_BRUTEFORCE]

# --- REGEX
URL_CHECKING_PATTERN = r'^(?:[a-zA-Z0-9_-]+\.)+[a-zA-Z0-9_-]+(?::\d+)?$'
URL_CHECKING_REGEX = re.compile(URL_CHECKING_PATTERN)
TRAILING_SLASH_PATTERN = "/$"
TRAILING_SLASH_REGEX = re.compile(TRAILING_SLASH_PATTERN)
PROTOCOL_PREFIX_PATTERN = "^(http|https)://"
PROTOCOL_PREFIX_REGEX = re.compile(PROTOCOL_PREFIX_PATTERN)

# --- LOGGING
# LOGGING_LEVEL_MODULES = "INFO"  # production
LOGGING_LEVEL_MODULES = "DEBUG"  # development
LOGGING_FORMAT_FILE = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
LOGGING_FILE_FORMAT = "%s%s_%s.log"
LOGGING_HANDLER_CLASS = "logging.FileHandler"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "file": {
            "format": LOGGING_FORMAT_FILE
        }
    },
    "handlers": {
        "steering_module": {
            "level": LOGGING_LEVEL_MODULES,
            "class": LOGGING_HANDLER_CLASS,
            "filename": (LOGGING_FILE_FORMAT % (LOGGING_DIR, CURRENT_DATE, STEERING_MODULE)),
            "formatter": "file"
        },
        "directory_bruteforce": {
            "level": LOGGING_LEVEL_MODULES,
            "class": LOGGING_HANDLER_CLASS,
            "filename": (LOGGING_FILE_FORMAT % (LOGGING_DIR, CURRENT_DATE, DIRECTORY_BRUTEFORCE)),
            "formatter": "file"
        },
        "task_queue": {
            "level": LOGGING_LEVEL_MODULES,
            "class": LOGGING_HANDLER_CLASS,
            "filename": (LOGGING_FILE_FORMAT % (LOGGING_DIR, CURRENT_DATE, TASK_QUEUE)),
            "formatter": "file"
        },
        "request_manager": {
            "level": LOGGING_LEVEL_MODULES,
            "class": LOGGING_HANDLER_CLASS,
            "filename": (LOGGING_FILE_FORMAT % (LOGGING_DIR, CURRENT_DATE, REQUEST_MANAGER)),
            "formatter": "file"
        },
    },
    "loggers": {
        "steering_module": {
            "handlers": ["steering_module"],
            "level": LOGGING_LEVEL_MODULES,
            "propagate": True,
        },
        "directory_bruteforce": {
            "handlers": ["directory_bruteforce"],
            "level": LOGGING_LEVEL_MODULES,
            "propagate": True,
        },
        "task_queue": {
            "handlers": ["task_queue"],
            "level": LOGGING_LEVEL_MODULES,
            "propagate": True,
        },
        "request_manager": {
            "handlers": ["request_manager"],
            "level": LOGGING_LEVEL_MODULES,
            "propagate": True,
        },
    },
}

log_conf.dictConfig(config=LOGGING)
steering_module_logger = logging.getLogger("steering_module")
bruteforce_logger = logging.getLogger("directory_bruteforce")
task_queue_logger = logging.getLogger("task_queue")
request_manager_logger = logging.getLogger("request_manager")
