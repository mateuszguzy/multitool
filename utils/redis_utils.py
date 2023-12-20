import time

from config.settings import (
    DB_INPUT_MODULE_MAPPER,
    REDIS_USER_INPUT_KEY,
    REDIS_MODULES_KEY,
    REDIS_TARGETS_KEY,
    ZAP_SPIDER,
    PUBSUB_LAST_MESSAGE_TIME_KEY,
)
from modules.helper.redis_client import RedisClient
from modules.zap.zap import zap


def prepare_final_results_dictionary() -> dict:
    """
    Pull all stored results from Redis and return in form of following dictionary:

    target_url: {
        module_producing_results: [ list_of_results ]
    }
    """
    results: dict = dict()

    with RedisClient() as rc:
        keys = rc.keys(f"{REDIS_USER_INPUT_KEY}{REDIS_MODULES_KEY}*")
        used_modules = rc.mget(keys)

        keys = rc.keys(f"{REDIS_USER_INPUT_KEY}{REDIS_TARGETS_KEY}*")
        targets = rc.mget(keys)

        for target in targets:
            target = target.decode("utf-8")
            results[target] = {}

            for used_module in used_modules:
                used_module = used_module.decode("utf-8")
                phase = used_module.split("|")[0]
                module = used_module.split("|")[1]

                keys = rc.keys(f"{target}*|{phase}|{module}|*")

                if not results[target].get(phase):
                    results[target][phase] = {}

                if module == ZAP_SPIDER:
                    results[target][phase][module] = zap.spider.all_urls
                else:
                    results[target][phase][module] = [
                        result.decode("utf-8") for result in rc.mget(keys)
                    ]

        rc.flushall()

    return results


def store_module_results_in_database(
    target: str, results: dict, phase: str, module: str
) -> None:
    """
    Stare results in Redis in form of following dictionary:

    target_url: {
        module_producing_results: {
            id: result
        }
    }
    """
    if results:
        with RedisClient() as rc:
            rc.mset(
                {f"{target}|{phase}|{module}|" + str(k): v for k, v in results.items()}
            )


def put_single_value_in_db(key: str, value: str) -> None:
    """
    Puts single key data in the database.
    """
    with RedisClient() as rc:
        rc.set(name=key, value=value)


def pull_single_value_from_db(key: str) -> str:
    """
    Pulls single key data from the database.
    """
    with RedisClient() as rc:
        return rc.get(key).decode("utf-8")


def withdraw_input_from_db(module: str) -> dict:
    input_dict: dict = dict()

    if module in DB_INPUT_MODULE_MAPPER:
        with RedisClient() as rc:
            # cannot decode results from Redis directly here because some results are
            # single values and some are lists e.g. port_scan::ports, so it's done while
            # creating input class
            input_dict = {
                k: rc.mget(rc.keys(f"{DB_INPUT_MODULE_MAPPER[module]['path']}{v}*"))
                for k, v in DB_INPUT_MODULE_MAPPER[module]["keys"].items()
            }

    return input_dict


def save_message_time():
    """
    Saves the time of the last message received from the broker.
    Used to check if the broker is still alive.
    """
    put_single_value_in_db(key=PUBSUB_LAST_MESSAGE_TIME_KEY, value=str(time.time()))
