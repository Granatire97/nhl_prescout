from aioresponses import aioresponses
from pipeline.client import fetch_many
import pytest
from yarl import URL as YarlURL

URL = "https://example.test/data"
URL_2 = "https://example.test/other"

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

async def test_default_raises():
    with aioresponses() as mock:
        mock.get(URL, payload={"ok": True})
        mock.get(URL_2, status=404)

        with pytest.raises(ValueError, match="Not found") as e:
            result = await fetch_many([URL, URL_2], min_delay=0)

    assert f"Not found: {URL_2}" in str(e.value)
    assert len(mock.requests[("GET", YarlURL(URL_2))]) == 1

async def test_return_exceptions():
    with aioresponses() as mock:
        mock.get(URL, payload={"ok": True})
        mock.get(URL_2, status=404)

        result = await fetch_many([URL, URL_2], min_delay=0, return_exceptions=True)

    assert result[0] == {"ok": True}
    assert isinstance(result[1], ValueError)