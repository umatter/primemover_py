from src.Info import *
class Crawler:
    def __init__(self, crawler_info=None,name=None, description=None,                  ):
        self.crawler_info = crawler_info
        self._description = description
        self._name = name
        self.queues = []

    @property
    def crawler_info(self):
        return self._crawler_info

    @crawler_info.setter
    def crawler_info(self, info):
        if not type(info) is CrawlerInfo:
            raise TypeError('crawler_info must be of type QueueInfo')
        else:
            self._crawler_info = info

    def __str__(self):
        crawler_descr = \
            f'"id": {self.crawler_info.crawler_id or ""},\n' \
            f'"user_id": "{self.crawler_info._user_id or ""}",\n' \
            f'"configuration_id": "{self.crawler_info.configuration_id or ""}",\n' \
            f'"proxy_id": "{self.crawler_info.proxy_id or ""}",\n' \
            f'"agent_id": "{self.crawler_info.agent_id or ""}",\n' \
            f'"name": "{self._name or ""}",\n' \
            f'"description": "{self._description or ""}",\n' \
            f'"active": {self.crawler_info.active or ""}'

        formatted = ",\n".join([str(x) for x in self.queues])
        return f'{{{crawler_descr},"queues": [\n{formatted}]}}'
