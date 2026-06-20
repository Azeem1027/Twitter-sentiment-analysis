import requests


DEFAULT_XQUIK_BASE_URL = "https://xquik.com/api/v1"


def fetch_xquik_tweets(
    query,
    api_key,
    limit=20,
    base_url=DEFAULT_XQUIK_BASE_URL,
    http_get=requests.get,
):
    clean_query = query.strip()
    clean_key = api_key.strip()
    if not clean_query or not clean_key:
        return []

    response = http_get(
        f"{base_url.rstrip('/')}/x/tweets/search",
        headers={"x-api-key": clean_key},
        params={"q": clean_query, "queryType": "Latest", "limit": limit},
        timeout=15,
    )
    response.raise_for_status()

    rows = []
    for tweet in response.json().get("tweets", []):
        if not isinstance(tweet, dict):
            continue

        text = tweet.get("text")
        if not isinstance(text, str) or not text.strip():
            continue

        rows.append(
            {
                "Tweet": text,
                "Author": _author(tweet),
                "Created At": tweet.get("createdAt", ""),
                "URL": _tweet_url(tweet),
            }
        )

    return rows


def _author(tweet):
    for key in ("username", "userName", "authorUsername"):
        value = tweet.get(key)
        if isinstance(value, str) and value:
            return value

    author = tweet.get("author")
    if isinstance(author, dict):
        for key in ("username", "userName", "screenName", "name"):
            value = author.get(key)
            if isinstance(value, str) and value:
                return value

    return "unknown"


def _tweet_url(tweet):
    value = tweet.get("url")
    if isinstance(value, str) and value:
        return value

    tweet_id = tweet.get("id") or tweet.get("tweetId")
    if tweet_id is None:
        return ""

    return f"https://x.com/i/status/{tweet_id}"
