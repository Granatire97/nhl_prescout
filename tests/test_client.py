from aioresponses import aioresponses
from pipeline.client import fetch_many
import pytest
from yarl import URL as YarlURL

URL = "https://example.test/data"

async def test_success():
    with aioresponses() as mock:
        mock.get(URL, payload={"ok": True})
        result = await fetch_many([URL], min_delay=0)
    assert result == [{"ok": True}]

async def test_retry_success():
    with aioresponses() as mock:
        mock.get(URL, status=500)
        mock.get(URL, status=200, payload={"ok": True})
        result = await fetch_many([URL], min_delay=0)
    assert result == [{"ok": True}]

async def test_retry_exhausted():
    with aioresponses() as mock:
        mock.get(URL, status=500)
        mock.get(URL, status=500)
        mock.get(URL, status=500)

        with pytest.raises(RuntimeError) as e:
            await fetch_many([URL], min_delay=0, retries=3)
    assert f"Failed after 3 tries: {URL}" in str(e.value)
    assert len(mock.requests[("GET", YarlURL(URL))]) == 3

async def test_status_404():
    with aioresponses() as mock:
        mock.get(URL, status=404)

        with pytest.raises(ValueError, match="Not found") as e:
            await fetch_many([URL], min_delay=0)
    assert f"Not found: {URL}" in str(e.value)
    assert len(mock.requests[("GET", YarlURL(URL))]) == 1

async def test_invalid_JSON():
    with aioresponses() as mock:
        mock.get(URL, body="<html>")

        with pytest.raises(ValueError, match="Invalid JSON") as e:
            await fetch_many([URL], min_delay=0)
    assert f"Invalid JSON from {URL}" in str(e.value)