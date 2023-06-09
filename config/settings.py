import multiprocessing
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- GENERAL
NUMBER_OF_AVAILABLE_CPU_CORES = multiprocessing.cpu_count() + 2

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

# --- CONTAINERS
# RABBITMQ
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST")

# CELERY
CELERY_FLOWER_ADDRESS = os.getenv("CELERY_FLOWER_ADDRESS")
CELERY_FLOWER_PORT = os.getenv("CELERY_FLOWER_PORT")
