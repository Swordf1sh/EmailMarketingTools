import asyncio
import re
from urllib.parse import urlparse, urljoin, urlunparse

import aiohttp
from bs4 import BeautifulSoup


class AsyncEmailScraper:

    def __init__(self, base_url, max_pages=100, max_workers=50):
        self.base_url = base_url
        self.visited_urls = set()
        self.max_pages = max_pages
        self.emails = set()
        self.to_visit_urls = asyncio.Queue()
        self.max_workers = max_workers
        self.semaphore = asyncio.Semaphore(max_workers)

    async def fetch(self, url):
        async with self.semaphore:
            try:
                async with self.session.get(url) as response:
                    # response.raise_for_status()
                    result = await response.text()
                    self.visited_urls.add(url)
                    return result
            except aiohttp.ClientError as e:
                print(f"Failed to fetch {url}: {e}")
                self.visited_urls.add(url)
                return ""

    async def extract_emails(self, content):
        emails_set = set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", content))
        self.emails.update(emails_set)

    def clean_url(self, url):
        return urlunparse(url._replace(query='', fragment=''))

    async def extract_links(self, _url, content):
        domain = urlparse(_url).netloc
        soup = BeautifulSoup(content, 'html.parser')
        for anchor in soup.find_all('a', href=True):
            link = anchor['href']
            if not urlparse(link).netloc:
                link = urljoin(_url, link)
            cleaned_url = self.clean_url(urlparse(link))
            if (domain == urlparse(cleaned_url).netloc and cleaned_url not in self.visited_urls and
                    len(self.visited_urls) < self.max_pages):
                await self.to_visit_urls.put(cleaned_url)

    async def worker(self):
        while True:
            url = await self.to_visit_urls.get()
            if url not in self.visited_urls:
                self.visited_urls.add(url)
                content = await self.fetch(url)
                if content:
                    await self.extract_links(url, content)
                    await self.extract_emails(content)
            self.to_visit_urls.task_done()
            if self.to_visit_urls.empty() and len(self.visited_urls) >= self.max_pages:
                break

    async def run(self):
        async with aiohttp.ClientSession() as self.session:
            await self.to_visit_urls.put(self.base_url)
            workers = [asyncio.create_task(self.worker()) for _ in range(self.max_workers)]
            await self.to_visit_urls.join()
            for worker in workers:
                worker.cancel()
            await asyncio.gather(*workers, return_exceptions=True)


import time


async def main():
    start = time.time()
    scraper = AsyncEmailScraper(
        "https://oned.ge", max_workers=100, max_pages=100)
    await scraper.run()
    print(f"Found emails: {scraper.emails}")
    print(f"Time taken: {time.time() - start} seconds")


if __name__ == "__main__":
    asyncio.run(main())
