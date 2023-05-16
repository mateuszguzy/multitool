from pathlib import Path

# --- DIRECTORIES
BASE_DIR = Path(__file__).resolve().parent.parent
WORDLISTS_DIR = f"{BASE_DIR}/utils/wordlists"
LOG_DIR = f"{BASE_DIR}/logs/"

# --- STEERING MODULE
RECON_PHASE_MODULES = ["dir_bruteforce", "email_scraping", "credential_leaks_check"]
SCAN_PHASE_MODULES = ["port_scan", "file_upload_form", "file_inclusion_url"]

# --- LOGGING
LOGGING_LEVEL = "DEBUG"  # development
# LOGGING_LEVEL = "INFO"  # production
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
