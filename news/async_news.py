import aiohttp
import asyncio
import urllib.parse
import feedparser


async def fetch_rss(session, ticker, limit):
    query = urllib.parse.quote(f"{ticker} stock")

    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

    async with session.get(url) as resp:
        text = await resp.text()
        feed = feedparser.parse(text)

        headlines = []
        seen = set()

        for entry in feed.entries:
            title = entry.get("title", "").strip()
            key = title.lower()

            if title and key not in seen:
                seen.add(key)
                headlines.append(title)

            if len(headlines) >= limit:
                break

        return ticker, headlines


async def get_all_news(tickers, limit):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_rss(session, t, limit) for t in tickers]
        results = await asyncio.gather(*tasks)

    return dict(results)