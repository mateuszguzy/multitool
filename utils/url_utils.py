from typing import List, Set, Optional
from urllib.parse import urlparse


def url_formatter(input_target: str, module: Optional[str] = None) -> str:
    """
    Format URL to be in form of http://target
    """
    final_url = ""
    url = urlparse(input_target)

    if not url.scheme and url.path:
        path = url.path
        url = url._replace(netloc=path, path="", scheme="http")

    if module == "port_scan":
        if url.scheme:
            url = url._replace(scheme="", path="")
            final_url = url.netloc + url.path
    else:
        final_url = url.geturl()

    return final_url


def transform_regexs_into_urls(targets: List[str]) -> Set[str]:
    """
    Function responsible for transforming regexs into urls.
    """
    result_targets = set()

    for target in targets:
        target = target.replace(".*", "")
        result_targets.add(target)

    return result_targets
