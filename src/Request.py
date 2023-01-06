import aiohttp
from Main import *
from aiohttp import ContentTypeError


class Request:
    headers = {
        'Referer': 'https://www.pixiv.net',
        'User-Agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.54'
    }
    resp_list = {}

    @classmethod
    def __init__(cls, url_list):
        cls.resp_list = cls.download(url_list)

    @classmethod
    def download(cls, url_list):
        html_list, bina_list, json_list = [], [], []

        async def _except(_url):
            async with aiohttp.ClientSession() as asy_spider:
                async with await asy_spider.get(url=_url[0], headers=cls.headers) as resp:
                    try:
                        html = await resp.text()
                        html_list.append(html)
                    except ContentTypeError:
                        pass
                    except UnicodeDecodeError:
                        pass
                    try:
                        bina = await resp.read()
                        bina_list.append(bina)
                    except ContentTypeError:
                        pass
                    try:
                        _json = await resp.json()
                        json_list.append(_json)
                    except ContentTypeError:
                        pass

        asy_launch(_except, (url_list,), call_back=None)
        return {'html': html_list, 'bina': bina_list, 'json': json_list}
