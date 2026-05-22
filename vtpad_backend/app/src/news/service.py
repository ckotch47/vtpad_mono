import requests
from app.src import common


class NewsService:
    http_timeout = 6

    def __init__(self):
        self.req = requests
        self.config = common.EnvConfig()

    async def get_news_for_user(self, user: dict):
        try:
            temp = self.req.get(url=f"{self.config.news_url}/news/all", timeout=self.http_timeout)
            # params={"user_id":user.get('id')})
            if temp.status_code == 200:
                return temp.json()
            return []
        except:
            return []

    async def read_news(self, news: str, user: dict):
        try:
            temp = self.req.patch(url=f"{self.config.news_url}/news/read",
                                  params={
                                      "user_id": user.get('id'),
                                      "news_id": news
                                  },
                                  timeout=self.http_timeout)
            if temp.status_code == 200:
                return temp.json()
            return []

        except:
            return []

    async def get_unread_count(self, user: dict):
        try:
            temp = self.req.get(url=f"{self.config.news_url}/news/unread-count",
                                params={"user_id": user.get('id')}, timeout=self.http_timeout)
            if temp.status_code == 200:
                return temp.json()
            return []
        except:
            return []
