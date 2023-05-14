from pathlib import Path

# --- DIRECTORIES
BASE_DIR = Path(__file__).resolve().parent
WORDLISTS_DIR = "/utils/wordlists"

# --- STEERING MODULE
RECON_PHASE_MODULES = ["dir_bruteforce", "email_scraping", "credential_leaks_check"]
SCAN_PHASE_MODULES = ["port_scan", "file_upload_form", "file_inclusion_url"]
