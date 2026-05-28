import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote
import re
from collections import deque

BASE = "http://www.fawanews.sc/"
DOMAIN = "fawanews.sc"

visited = set()
queue = deque([BASE])

headers = {
    "User-Agent": "Mozilla/5.0"
}

m3u8_regex = re.compile(r'https?://[^\s\'"]+\.m3u8[^\s\'"]*')

results = {}

def get_title(url):
    path = urlparse(url).path
    name = path.split("/")[-1].replace(".html", "")
    return unquote(name)

def same_domain(url):
    return DOMAIN in urlparse(url).netloc

while queue:
    url = queue.popleft()

    if url in visited:
        continue

    visited.add(url)

    try:
        r = requests.get(url, headers=headers, timeout=10)

        if r.status_code != 200:
            continue

        html = r.text
        soup = BeautifulSoup(html, "html.parser")

        # ambil m3u8 dari HTML
        m3u8_links = set(m3u8_regex.findall(html))

        # ambil dari JS
        for script in soup.find_all("script", src=True):
            try:
                js_url = urljoin(url, script["src"])
                js = requests.get(js_url, headers=headers, timeout=10).text
                m3u8_links.update(m3u8_regex.findall(js))
            except:
                pass

        # simpan hasil
        if m3u8_links:
            title = get_title(url)
            for m in m3u8_links:
                results[title] = m

        # crawl link lain
        for a in soup.find_all("a", href=True):
            link = urljoin(url, a["href"])
            if same_domain(link) and link not in visited:
                queue.append(link)

    except:
        pass

# =========================
# OUTPUT FILE
# =========================
with open("pakwa.txt", "w", encoding="utf-8") as f:
    for title, stream in results.items():
        f.write(f"{title},{stream}\n")

print(f"Done. Total: {len(results)}")
