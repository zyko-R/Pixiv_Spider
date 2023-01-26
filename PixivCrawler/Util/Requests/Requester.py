from abc import abstractmethod, ABC

from aiohttp import ContentTypeError, TCPConnector, ClientSession

from PixivCrawler.Util.ThreadManager import ThreadLauncher, Async


def colour_str(message, code, form=0):
    return f'\033[{form};{code}m{message}\033[0m'


class IDownloader(ABC):
    @abstractmethod
    def response(self, url_list):
        pass


class Requester(IDownloader):
    headers = {
        'Referer': 'https://www.pixiv.net',
        'User-Agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.54'
    }

    def request(self, url_list):
        resp_list = {'html': [], 'bina': [], 'json': []}

        async def download(url):
            async with ClientSession(connector=TCPConnector(ssl=False)) as async_spider:
                async with await async_spider.get(url=url, headers=self.headers) as resp:
                    parse_list = {'html': resp.text, 'json': resp.json, 'bina': resp.read}
                    for tag in parse_list.keys():
                        try:
                            resp_list[tag].append(await parse_list[tag]())
                        except (ContentTypeError, UnicodeDecodeError):
                            resp_list[tag].append(None)

        ThreadLauncher(Async(download, (url_list,)))
        return resp_list

    def response(self, url_list):
        resp = self.request(url_list)
        return resp
