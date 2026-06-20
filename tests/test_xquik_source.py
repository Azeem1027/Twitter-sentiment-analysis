import unittest

from xquik_source import fetch_xquik_tweets


class FakeResponse:
    def __init__(self, data):
        self.data = data

    def raise_for_status(self):
        return None

    def json(self):
        return self.data


class FakeGet:
    def __init__(self, data):
        self.data = data
        self.calls = []

    def __call__(self, url, *, headers, params, timeout):
        self.calls.append(
            {
                "url": url,
                "headers": headers,
                "params": params,
                "timeout": timeout,
            }
        )
        return FakeResponse(self.data)


class XquikSourceTest(unittest.TestCase):
    def test_fetch_xquik_tweets_maps_response_rows(self):
        fake_get = FakeGet(
            {
                "tweets": [
                    {
                        "id": "123",
                        "text": "Great dashboard launch",
                        "createdAt": "2026-06-20T12:00:00Z",
                        "username": "example",
                    }
                ]
            }
        )

        rows = fetch_xquik_tweets(
            "dashboard",
            "test-key",
            limit=5,
            base_url="https://xquik.com/api/v1",
            http_get=fake_get,
        )

        self.assertEqual(
            rows,
            [
                {
                    "Tweet": "Great dashboard launch",
                    "Author": "example",
                    "Created At": "2026-06-20T12:00:00Z",
                    "URL": "https://x.com/i/status/123",
                }
            ],
        )
        self.assertEqual(fake_get.calls[0]["url"], "https://xquik.com/api/v1/x/tweets/search")
        self.assertEqual(fake_get.calls[0]["headers"], {"x-api-key": "test-key"})
        self.assertEqual(fake_get.calls[0]["params"]["q"], "dashboard")
        self.assertEqual(fake_get.calls[0]["params"]["queryType"], "Latest")
        self.assertEqual(fake_get.calls[0]["params"]["limit"], 5)

    def test_fetch_xquik_tweets_requires_query_and_key(self):
        fake_get = FakeGet({"tweets": []})

        self.assertEqual(fetch_xquik_tweets("", "test-key", http_get=fake_get), [])
        self.assertEqual(fetch_xquik_tweets("topic", "", http_get=fake_get), [])
        self.assertEqual(fake_get.calls, [])


if __name__ == "__main__":
    unittest.main()
