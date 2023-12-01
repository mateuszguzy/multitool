import urllib.parse

from config.settings import steering_module_logger
from modules.zap.zap import zap

logger = steering_module_logger


def set_user_auth_config_for_dvwa(context_id: int) -> int:
    """
    Set user authentication configuration for ZAP.
    DVWA ONLY RIGHT NOW
    """
    user = "Administrator"
    username = "admin"
    password = "password"

    user_id = zap.users.new_user(context_id, user)
    user_auth_config = (
        "Username="
        + urllib.parse.quote(username)
        + "&Password="
        + urllib.parse.quote(password)
    )
    zap.users.set_authentication_credentials(
        contextid=context_id,
        userid=user_id,
        authcredentialsconfigparams=user_auth_config,
    )
    zap.users.set_user_enabled(contextid=context_id, userid=user_id, enabled="true")
    zap.forcedUser.set_forced_user(contextid=context_id, userid=user_id)
    zap.forcedUser.set_forced_user_mode_enabled("true")
    logger.debug("CREATED::User authentication configuration for DVWA")

    return user_id
