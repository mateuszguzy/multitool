from config.settings import (
    ZAP_AUTHENTICATION_SCRIPT_NAME,
    ZAP_AUTHENTICATION_SCRIPT_PATH,
    steering_module_logger,
)
from modules.zap.zap import zap

logger = steering_module_logger


def upload_authentication_script_for_dvwa():
    script_type = "authentication"
    script_engine = "Oracle Nashorn"
    charset = "UTF-8"

    if not check_if_script_is_already_uploaded(
        file_name=ZAP_AUTHENTICATION_SCRIPT_NAME
    ):
        zap.script.load(
            scriptname=ZAP_AUTHENTICATION_SCRIPT_NAME,
            scripttype=script_type,
            scriptengine=script_engine,
            filename=ZAP_AUTHENTICATION_SCRIPT_PATH,
            charset=charset,
        )
        logger.info(f"UPLOADED::SCRIPT::{ZAP_AUTHENTICATION_SCRIPT_NAME}")

    else:
        logger.warning(f"SCRIPT::{ZAP_AUTHENTICATION_SCRIPT_NAME} is already loaded")


def check_if_script_is_already_uploaded(file_name: str) -> bool:
    loaded_scripts = zap.script.list_scripts
    for script in loaded_scripts:
        if script.get("name") == file_name:
            return True
    return False
