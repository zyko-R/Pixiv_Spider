import asyncio
from enum import Enum

from aiohttp import TCPConnector, ClientSession

from PixivCrawler.Downloader.Lib.Plugins import *


def colour_str(message, code, form=0):
    return f'\033[{form};{code}m{message}\033[0m'


class Mode(Enum):
    HTML, JSON, BYTE = 'HTML', 'JSON', 'BYTE'


class Request:
    headers = {
        'Referer': 'https://www.pixiv.net',
        'User-Agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.54'
    }

    def __new__(cls, url_list: list, mode: Mode):
        self = super(Request, cls).__new__(cls)
        self.urls, self.MODE, self.resp_list = url_list, mode, []
        self.get()
        return self.resp_list

    @Login.Wrapper(auto_login=False)
    def get(self):
        async def download_ea(url):
            async with ClientSession(connector=TCPConnector(ssl=False)) as async_spider:
                async with await async_spider.get(url=url, headers=self.headers) as resp:
                    get = {Mode.HTML: resp.text, Mode.JSON: resp.json, Mode.BYTE: resp.read}
                    self.resp_list.append(await get[self.MODE]())
        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)
        task_list = [loop.create_task(download_ea(url)) for url in self.urls]
        try:
            loop.run_until_complete(asyncio.wait(task_list))
        except ValueError:
            pass

