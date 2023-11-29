from zapv2 import ZAPv2  # type: ignore

from config.settings import ZAP_EXPOSED_PORT, ZAP_API_KEY

zap = ZAPv2(
    apikey=ZAP_API_KEY,
    proxies={
        "http": f"http://zap:{ZAP_EXPOSED_PORT}",
        "https": f"https://zap:{ZAP_EXPOSED_PORT}",
    },
)
