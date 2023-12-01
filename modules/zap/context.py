import ast
from typing import List

from config.settings import steering_module_logger
from modules.zap.zap import zap

logger = steering_module_logger


def create_new_context(context_name: str) -> int:
    try:
        zap.context.new_context(context_name)
        context = get_context(context_name)
        context_id = context.get("id")
        logger.info(f"CREATED::CONTEXT::{context_name}")

        return context_id if context_id else None

    except Exception as e:
        logger.error(
            f"ERROR::CONTEXT::{context_name}::Could not create context with name {e}"
        )
        raise ValueError(f"Could not create context with name: {context_name} {e}")


def get_context(context_name: str) -> dict:
    return zap.context.context(context_name)


def include_in_context(target: str, context_name: str) -> None:
    context = get_context(context_name)
    include_url = f"{target}.*"

    if not target_in_included_regexs(target=include_url, context=context):
        try:
            zap.context.include_in_context(context_name, include_url)
            logger.info(f"INCLUDED::CONTEXT::{include_url}")
        except Exception as e:
            logger.error(f"CONTEXT::{include_url}::{e}")

    else:
        logger.warning(f"CONTEXT::{include_url}::Already in context")


def exclude_from_context(targets: List[str], context_name: str) -> None:
    for target in targets:
        if not target_in_excluded_regexs(
            target=target, context=get_context(context_name)
        ):
            try:
                zap.context.exclude_from_context(context_name, target)
                logger.info(f"EXCLUDED::CONTEXT::{target}")
            except Exception as e:
                logger.error(f"CONTEXT::{target}::{e}")


def target_in_included_regexs(target: str, context: dict) -> bool:
    """
    Safety pillow to prevent adding the same target to the same context multiple times.
    """
    included_regexs = ast.literal_eval(context.get("includeRegexs", []))

    for regex in included_regexs:
        if target in regex:
            return True

    return False


def target_in_excluded_regexs(target: str, context: dict) -> bool:
    """
    Safety pillow to prevent excluding the same target from the same context multiple times.
    """
    included_regexs = ast.literal_eval(context.get("excludeRegexs", []))

    for regex in included_regexs:
        if target in regex:
            logger.warning(f"CONTEXT::{target}::Already excluded from context")
            return True

    return False
