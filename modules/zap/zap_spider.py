import time
import uuid
from typing import List, Optional

from config.settings import zap_spider_logger, RECON_PHASE, ZAP_SPIDER
from modules.task_queue.tasks import log_results
from modules.zap.zap import zap
from utils.custom_dataclasses import ResultEvent
from utils.utils import convert_list_or_set_to_dict, store_module_results_in_database

logger = zap_spider_logger


def start_zap_spider(
    target_url: str,
    context_id: Optional[int] = None,
    user_id: Optional[int] = None,
    as_user: bool = False,
) -> None:
    if as_user and context_id and user_id:
        scan_id = zap.spider.scan_as_user(context_id, user_id, target_url)
    else:
        scan_id = zap.spider.scan(target_url)

    logger.debug(f"START::zap_spider::{scan_id}")

    log_zap_spider_progress(scan_id=scan_id)
    spider_results = zap.spider.results(scan_id)

    if len(spider_results) > 0:
        logger.debug(f"{spider_results}")
        save_zap_spider_results(spider_results=spider_results, target=target_url)

        for result in spider_results:
            event = ResultEvent(
                id=uuid.uuid4(),
                source_module=__name__,
                target=target_url,
                result=result,
            )
            log_results.delay(event=event)


def log_zap_spider_progress(scan_id: int) -> None:
    while int(zap.spider.status(scan_id)) < 100:
        logger.debug(f"RUN::{scan_id}::{zap.spider.status(scan_id)}%")
        time.sleep(1)


def save_zap_spider_results(spider_results: List[str], target: str) -> None:
    results = convert_list_or_set_to_dict(list_of_items=spider_results)
    store_module_results_in_database(
        target=target,
        results=results,
        phase=RECON_PHASE,
        module=ZAP_SPIDER,
    )
