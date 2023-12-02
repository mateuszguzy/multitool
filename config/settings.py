import datetime
import logging
import logging.config as log_conf
import multiprocessing
import os
from pathlib import Path

from dotenv import load_dotenv
from kombu.serialization import register  # type: ignore

load_dotenv()

# --- GENERAL
NUMBER_OF_AVAILABLE_CPU_CORES = multiprocessing.cpu_count() + 2
CURRENT_DATE = datetime.datetime.utcnow().strftime("%Y%m%d")
MAX_RECURSION_DEPTH = 6
GET_REQUEST_TIMEOUT = 5
SECONDS_TO_WAIT_FOR_MESSAGES_BEFORE_CLOSING = 10

# --- DIRECTORIES
BASE_DIR = Path(__file__).resolve().parent.parent
WORDLISTS_DIR = f"{BASE_DIR}/utils/wordlists"
LOGGING_DIR = f"{BASE_DIR}/logs/{CURRENT_DATE}/"
TESTS_MOCKED_INPUT_DIR = f"{BASE_DIR}/tests/mocked_user_input"
WORKFLOW_YAML_PATH = f"{BASE_DIR}/config/workflow.yaml"

# --- MODULES
# STEERING_MODULE
STEERING_MODULE = "steering_module"

# TASK_QUEUE
TASK_QUEUE = "task_queue"

# -- MANAGERS
REQUEST_MANAGER = "request_manager"
SOCKET_MANAGER = "socket_manager"

# -- SCAN_PHASE
SCAN_PHASE = "scan"
# PORT_SCAN
PORT_SCAN = "port_scan"
IMPORTANT_PORTS = {
    21,
    22,
    23,
    25,
    53,
    80,
    110,
    111,
    135,
    139,
    143,
    443,
    445,
    993,
    995,
    1723,
    3306,
    3389,
    5900,
    8080,
}

# -- RECON_PHASE
RECON_PHASE = "recon"

# CRAWLING
ZAP_SPIDER = "zap_spider"

# DIRECTORY_BRUTEFORCE
DIRECTORY_BRUTEFORCE = "directory_bruteforce"
DIRECTORY_BRUTEFORCE_REQUEST_METHOD = "GET"

# EMAIL_SCRAPER
EMAIL_SCRAPER = "email_scraper"
EMAIL_SCRAPER_REGEX_PATTERN = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"

# --- GAIN_ACCESS_PHASE
GAIN_ACCESS_PHASE = "gain_access"
# LFI
LFI = "lfi"
LFI_REQUEST_METHOD = "GET"

# --- ZAP
ZAP_API_KEY = os.getenv("ZAP_API_KEY")
ZAP_EXPOSED_PORT = int(os.getenv("ZAP_EXPOSED_PORT", 8080))
ZAP_AUTHENTICATION_SCRIPT_NAME = "auth-dvwa.js"
ZAP_AUTHENTICATION_SCRIPT_PATH = f"/zap/scripts/custom/{ZAP_AUTHENTICATION_SCRIPT_NAME}"

# All currently available modules
AVAILABLE_FUNCTIONALITY: dict = {
    RECON_PHASE: {
        ZAP_SPIDER,
        DIRECTORY_BRUTEFORCE,
        EMAIL_SCRAPER,
    },
    SCAN_PHASE: {
        PORT_SCAN,
    },
    GAIN_ACCESS_PHASE: {
        LFI,
    },
}
RECON_PHASE_MODULES = list(AVAILABLE_FUNCTIONALITY["recon"])
SCAN_PHASE_MODULES = list(AVAILABLE_FUNCTIONALITY["scan"])
GAIN_ACCESS_PHASE_MODULES = list(AVAILABLE_FUNCTIONALITY["gain_access"])
AVAILABLE_PHASES = list(AVAILABLE_FUNCTIONALITY.keys())
ALL_MODULES = {module for phase in AVAILABLE_FUNCTIONALITY.values() for module in phase}
RECON_PHASE_MODULES.sort()
SCAN_PHASE_MODULES.sort()
GAIN_ACCESS_PHASE_MODULES.sort()

# make sure user will not get tracebacks and similar data in terminal
# !! bash script will not treat those as vars only as a plain text
RESULTS_FOR_USER_FROM_MODULES = ["steering_module", "recon", "scan", "gain_access"]

# DB / REDIS
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_BROKER_BACKEND = os.getenv("CELERY_BROKER_BACKEND")
PUBSUB_RESULTS_CHANNEL_NAME = "results"
PUBSUB_LAST_MESSAGE_TIME_KEY = "last_message_time"
REDIS_USER_INPUT_KEY = "user_input|"
REDIS_TARGETS_KEY = "targets|"
REDIS_MODULES_KEY = "modules|"
REDIS_USE_TYPE_KEY = "use_type"
REDIS_OUTPUT_AFTER_EVERY_FINDING_KEY = "output_after_every_finding"
REDIS_RECON_INPUT_KEY = "recon|"
REDIS_DIRECTORY_BRUTEFORCE_KEY = "directory_bruteforce|"
REDIS_DIRECTORY_BRUTEFORCE_LIST_SIZE_KEY = "list_size"
REDIS_DIRECTORY_BRUTEFORCE_RECURSIVE_KEY = "recursive"
REDIS_DIRECTORY_BRUTEFORCE_INPUT_KEY = (
    f"{REDIS_USER_INPUT_KEY}{REDIS_RECON_INPUT_KEY}{REDIS_DIRECTORY_BRUTEFORCE_KEY}"
)
REDIS_SCAN_INPUT_KEY = "scan|"
REDIS_PORT_SCAN_KEY = "port_scan|"
REDIS_PORT_SCAN_TYPE_KEY = "type"
REDIS_PORT_SCAN_PORTS = "ports|"
REDIS_PORT_SCAN_INPUT_KEY = (
    f"{REDIS_USER_INPUT_KEY}{REDIS_SCAN_INPUT_KEY}{REDIS_PORT_SCAN_KEY}"
)
REDIS_ZAP_CONTEXT_KEY = "context|"
REDIS_ZAP_CONTEXT_ID_KEY = f"{REDIS_ZAP_CONTEXT_KEY}id"
REDIS_ZAP_CONTEXT_NAME_KEY = f"{REDIS_ZAP_CONTEXT_KEY}name"
REDIS_ZAP_USER_KEY = "user|"
REDIS_ZAP_USER_ID_KEY = f"{REDIS_ZAP_USER_KEY}id"
REDIS_ZAP_SPIDER_INPUT_KEY = "zap_spider|"
REDIS_ZAP_SPIDER_AS_USER_KEY = "as_user"
REDIS_ZAP_SPIDER_ENHANCED_KEY = "enhanced"

DB_INPUT_MODULE_MAPPER: dict = {
    ZAP_SPIDER: {
        "path": REDIS_ZAP_SPIDER_INPUT_KEY,
        "keys": {
            "as_user": REDIS_ZAP_SPIDER_AS_USER_KEY,
            "enhanced": REDIS_ZAP_SPIDER_ENHANCED_KEY,
        },
    },
    DIRECTORY_BRUTEFORCE: {
        "path": REDIS_DIRECTORY_BRUTEFORCE_INPUT_KEY,
        "keys": {
            "list_size": REDIS_DIRECTORY_BRUTEFORCE_LIST_SIZE_KEY,
            "recursive": REDIS_DIRECTORY_BRUTEFORCE_RECURSIVE_KEY,
        },
    },
    PORT_SCAN: {
        "path": REDIS_PORT_SCAN_INPUT_KEY,
        "keys": {
            "port_scan_type": REDIS_PORT_SCAN_TYPE_KEY,
            "ports": REDIS_PORT_SCAN_PORTS,
        },
    },
}


# --- LOGGING
# create loggers for every module separately but aggregate the outputs in files
# divided by core features and each module separately
LOGGING_LEVEL_MODULES = "DEBUG"  # development "INFO" for production
LOGGING_FORMAT_FILE = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
LOGGING_FILE_FORMAT = "%s%s_%s.log"
LOGGING_HANDLER_CLASS = "logging.FileHandler"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"file": {"format": LOGGING_FORMAT_FILE}},
    "handlers": {
        "steering_module": {
            "level": LOGGING_LEVEL_MODULES,
            "class": LOGGING_HANDLER_CLASS,
            "filename": (
                LOGGING_FILE_FORMAT % (LOGGING_DIR, CURRENT_DATE, STEERING_MODULE)
            ),
            "formatter": "file",
        },
        "directory_bruteforce": {
            "level": LOGGING_LEVEL_MODULES,
            "class": LOGGING_HANDLER_CLASS,
            "filename": (
                LOGGING_FILE_FORMAT % (LOGGING_DIR, CURRENT_DATE, RECON_PHASE)
            ),
            "formatter": "file",
        },
        "email_scraper": {
            "level": LOGGING_LEVEL_MODULES,
            "class": LOGGING_HANDLER_CLASS,
            "filename": (
                LOGGING_FILE_FORMAT % (LOGGING_DIR, CURRENT_DATE, RECON_PHASE)
            ),
            "formatter": "file",
        },
        "port_scan": {
            "level": LOGGING_LEVEL_MODULES,
            "class": LOGGING_HANDLER_CLASS,
            "filename": (LOGGING_FILE_FORMAT % (LOGGING_DIR, CURRENT_DATE, SCAN_PHASE)),
            "formatter": "file",
        },
        "lfi": {
            "level": LOGGING_LEVEL_MODULES,
            "class": LOGGING_HANDLER_CLASS,
            "filename": (
                LOGGING_FILE_FORMAT % (LOGGING_DIR, CURRENT_DATE, GAIN_ACCESS_PHASE)
            ),
            "formatter": "file",
        },
        "zap_spider": {
            "level": LOGGING_LEVEL_MODULES,
            "class": LOGGING_HANDLER_CLASS,
            "filename": (
                LOGGING_FILE_FORMAT % (LOGGING_DIR, CURRENT_DATE, RECON_PHASE)
            ),
            "formatter": "file",
        },
        "task_queue": {
            "level": LOGGING_LEVEL_MODULES,
            "class": LOGGING_HANDLER_CLASS,
            "filename": (
                LOGGING_FILE_FORMAT % (LOGGING_DIR, CURRENT_DATE, STEERING_MODULE)
            ),
            "formatter": "file",
        },
        "request_manager": {
            "level": LOGGING_LEVEL_MODULES,
            "class": LOGGING_HANDLER_CLASS,
            "filename": (
                LOGGING_FILE_FORMAT % (LOGGING_DIR, CURRENT_DATE, STEERING_MODULE)
            ),
            "formatter": "file",
        },
        "socket_manager": {
            "level": LOGGING_LEVEL_MODULES,
            "class": LOGGING_HANDLER_CLASS,
            "filename": (
                LOGGING_FILE_FORMAT % (LOGGING_DIR, CURRENT_DATE, STEERING_MODULE)
            ),
            "formatter": "file",
        },
        "dispatcher": {
            "level": LOGGING_LEVEL_MODULES,
            "class": LOGGING_HANDLER_CLASS,
            "filename": (
                LOGGING_FILE_FORMAT % (LOGGING_DIR, CURRENT_DATE, STEERING_MODULE)
            ),
            "formatter": "file",
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
        "email_scraper": {
            "handlers": ["email_scraper"],
            "level": LOGGING_LEVEL_MODULES,
            "propagate": True,
        },
        "port_scan": {
            "handlers": ["port_scan"],
            "level": LOGGING_LEVEL_MODULES,
            "propagate": True,
        },
        "lfi": {
            "handlers": ["lfi"],
            "level": LOGGING_LEVEL_MODULES,
            "propagate": True,
        },
        "zap_spider": {
            "handlers": ["zap_spider"],
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
        "socket_manager": {
            "handlers": ["socket_manager"],
            "level": LOGGING_LEVEL_MODULES,
            "propagate": True,
        },
        "dispatcher": {
            "handlers": ["dispatcher"],
            "level": LOGGING_LEVEL_MODULES,
            "propagate": True,
        },
    },
}

os.makedirs(LOGGING_DIR, exist_ok=True)
log_conf.dictConfig(config=LOGGING)
steering_module_logger = logging.getLogger("steering_module")
directory_bruteforce_logger = logging.getLogger("directory_bruteforce")
email_scraper_logger = logging.getLogger("email_scraper")
port_scan_logger = logging.getLogger("port_scan")
lfi_logger = logging.getLogger("lfi")
zap_spider_logger = logging.getLogger("zap_spider")
task_queue_logger = logging.getLogger("task_queue")
request_manager_logger = logging.getLogger("request_manager")
socket_manager_logger = logging.getLogger("socket_manager")
dispatcher_logger = logging.getLogger("dispatcher")

# Dictionary mapping module names to loggers
LOGGERS_MAPPER = {
    "__main__": steering_module_logger,
    ZAP_SPIDER: zap_spider_logger,
    DIRECTORY_BRUTEFORCE: directory_bruteforce_logger,
    EMAIL_SCRAPER: email_scraper_logger,
    PORT_SCAN: port_scan_logger,
    LFI: lfi_logger,
}
