import urllib.parse
from typing import Tuple

from config.settings import (
    ZAP_AUTHENTICATION_SCRIPT_NAME,
    REDIS_ZAP_CONTEXT_ID_KEY,
    steering_module_logger,
)
from modules.zap.script.script_dvwa import upload_authentication_script_for_dvwa
from modules.zap.users.users_dvwa import set_user_auth_config_for_dvwa
from modules.zap.zap import zap
from utils.utils import withdraw_single_data_from_db

logger = steering_module_logger


def set_logged_in_indicator_for_dvwa(context_id: int) -> None:
    logged_in_regex = '\\Q<a href="logout.php">Logout</a>\\E'
    logged_out_regex = '(?:Location: [./]*login\\.php)|(?:\\Q<form action="login.php" method="post">\\E)'

    zap.authentication.set_logged_in_indicator(context_id, logged_in_regex)
    zap.authentication.set_logged_out_indicator(context_id, logged_out_regex)
    logger.debug("CONFIGURED::logged in indicator regex for DVWA")


def set_script_based_auth_for_dvwa(target: str, context_id: int) -> None:
    post_data = (
        "username={%username%}&password={%password%}"
        + "&Login=Login&user_token={%user_token%}"
    )
    post_data_encoded = urllib.parse.quote(post_data)
    login_request_data = (
        f"scriptName={ZAP_AUTHENTICATION_SCRIPT_NAME}&Login_URL={target}/login.php&CSRF_Field=user_token"
        "&POST_Data=" + post_data_encoded
    )

    zap.authentication.set_authentication_method(
        contextid=context_id,
        authmethodname="scriptBasedAuthentication",
        authmethodconfigparams=login_request_data,
    )
    logger.debug("CONFIGURED::script based authentication for DVWA")


def prepare_authentication_for_dvwa(target: str) -> Tuple[int, int]:
    context_id = int(withdraw_single_data_from_db(key=f"{REDIS_ZAP_CONTEXT_ID_KEY}*"))

    upload_authentication_script_for_dvwa()
    set_script_based_auth_for_dvwa(target=target, context_id=context_id)
    set_logged_in_indicator_for_dvwa(context_id=context_id)
    user_id = set_user_auth_config_for_dvwa(context_id=context_id)

    return context_id, user_id
