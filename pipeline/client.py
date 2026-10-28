import json
import aiohttp
import asyncio
from tqdm.asyncio import tqdm_asyncio
import logging
import time


# Instantiate the module level logger
logger = logging.getLogger(__name__)

async def fetch_json(session, url, sem, retries=3, min_delay=0.5):
    async with sem:  # throttle concurrency
        for attempt in range(retries):
            try:
                await asyncio.sleep(min_delay)
                start = time.perf_counter()
                async with session.get(url, timeout=10) as resp:
                    logger.info(f"Operation took {time.perf_counter() - start:.4f} seconds")
                    logger.info(f"Run Information: url-{url}, status code-{resp.status}, attempt-{attempt + 1}")
                    if resp.status == 200:
                        text = await resp.text()
                        try:
                            return json.loads(text)
                        except json.JSONDecodeError as e:
                            raise ValueError(f"Invalid JSON from {url}") from e 
                    elif resp.status == 404:
                        raise ValueError(f"Not found: {url}")
                    else:
                        raise RuntimeError(f"HTTP {resp.status} from {url}")
            except ValueError as v:
                logger.warning(f"ERROR: {v}, Attempt: {attempt + 1} failed with {url}")
                raise
            except Exception as e:
                logger.warning(f"ERROR: {e}, Attempt: {attempt + 1} failed with {url}")
                if attempt == retries - 1:
                    raise RuntimeError(f"Failed after {retries} tries: {url}") from e
                await asyncio.sleep(2 ** attempt)

async def fetch_many(urls, concurrency=3, retries=3, min_delay=0.5, return_exceptions=False):
    sem = asyncio.Semaphore(concurrency)
    timeout = aiohttp.ClientTimeout(total=30)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async def safe_fetch(url):
            try:
                return await fetch_json(session, url, sem, retries=retries, min_delay=min_delay)
            except Exception as e:
                return e
        if return_exceptions:
            tasks = [safe_fetch(url) for url in urls]
        else: 
            tasks = [fetch_json(session, url, sem, retries=retries, min_delay=min_delay) for url in urls]


        results = await tqdm_asyncio.gather(*tasks)
        return results