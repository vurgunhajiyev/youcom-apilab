import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

YOU_API_KEY = "mykeypi"
SEARCH_URL = "https://ydc-index.io/v1/search"

HEADERS_BROWSER = {
    "User-Agent": "Mozilla/5.0"
}

def extract_image(page_url):
    try:
        r = requests.get(page_url, headers=HEADERS_BROWSER, timeout=6)
        soup = BeautifulSoup(r.text, "html.parser")

        # 1️⃣ og:image
        og = soup.find("meta", property="og:image")
        if og and og.get("content"):
            return og["content"]

        # 2️⃣ twitter:image
        tw = soup.find("meta", attrs={"name": "twitter:image"})
        if tw and tw.get("content"):
            return tw["content"]

        # 3️⃣ largest <img>
        images = soup.find_all("img")
        candidates = []

        for img in images:
            src = img.get("src")
            if not src:
                continue

            src = urljoin(page_url, src)

            try:
                w = int(img.get("width", 0))
                h = int(img.get("height", 0))
            except ValueError:
                w, h = 0, 0

            score = w * h
            candidates.append((score, src))

        if candidates:
            candidates.sort(reverse=True)
            return candidates[0][1]

    except Exception:
        pass

    return None


def search_with_images(query, count=5):
    headers = {
        "X-API-Key": YOU_API_KEY
    }

    params = {
        "query": query,
        "count": count
    }

    r = requests.get(SEARCH_URL, headers=headers, params=params)
    r.raise_for_status()

    results = r.json().get("results", {}).get("web", [])
    enriched = []

    for item in results:
        url = item.get("url")
        image = extract_image(url)

        enriched.append({
            "title": item.get("title"),
            "url": url,
            "image": image
        })

    return enriched


if __name__ == "__main__":
    data = search_with_images("artificial intelligence in healthcare", count=5)

    for d in data:
        print("\n---")
        print("TITLE:", d["title"])
        print("URL:", d["url"])
        print("IMAGE:", d["image"])
