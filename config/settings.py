import multiprocessing
import os
import re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- GENERAL
NUMBER_OF_AVAILABLE_CPU_CORES = multiprocessing.cpu_count() + 2

# DB / REDIS
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_DB = os.getenv("REDIS_DB")
REDIS_HOST = os.getenv("REDIS_HOST")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_BROKER_BACKEND = os.getenv("CELERY_BROKER_BACKEND")

# --- DIRECTORIES
BASE_DIR = Path(__file__).resolve().parent.parent
WORDLISTS_DIR = f"{BASE_DIR}/utils/wordlists"
LOG_DIR = f"{BASE_DIR}/logs/"

# --- MODULES
# STEERING
RECON_PHASE_MODULES = ["dir_bruteforce", "email_scraping", "credential_leaks_check"]
SCAN_PHASE_MODULES = ["port_scan", "file_upload_form", "file_inclusion_url"]

# DIRECTORY_BRUTEFORCE
DIR_BRUTEFORCE_REQUEST_METHOD = "GET"

# --- LOGGING
LOGGING_LEVEL = "DEBUG"  # development
# LOGGING_LEVEL = "INFO"  # production
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"

# --- REGEX
URL_CHECKING_PATTERN = "^[-a-zA-Z0-9@:%._\\+~#?&//=]{2,256}(?:\.[a-z]{2,6})?(?::\d+)?\\b([-a-zA-Z0-9@:%._\\+~#?&//=]*)$"
URL_CHECKING_REGEX = re.compile(URL_CHECKING_PATTERN)
TRAILING_SLASH_PATTERN = "/$"
TRAILING_SLASH_REGEX = re.compile(TRAILING_SLASH_PATTERN)
PROTOCOL_PREFIX_PATTERN = "^(http|https)://"
PROTOCOL_PREFIX_REGEX = re.compile(PROTOCOL_PREFIX_PATTERN)
