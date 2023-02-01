import re
from abc import abstractmethod

from lxml import etree

from PixivCrawler.Crawler.Prototype.IDHandler import ICrawler, IDHandler
from PixivCrawler.Downloader.Request import Request, Mode


def colorstr(message, code, form=0):
    return f'\033[{form};{code}m{message}\033[0m'


class IDPlugin(ICrawler):
    src_limit, file_name = 0, 'NOTSET'

    def __init__(self, handler: IDHandler, file_name: str): self.Handler, self.file_name = handler, file_name

    def crawl(self, file_name: None = None, id_list: None = None):
        def short(x): return x[:len(x) if len(x) < self.src_limit else self.src_limit]
        self.Handler.crawl(self.file_name, short(self.ids()))

    @abstractmethod
    def ids(self) -> []: pass


class ByAuthorID(IDPlugin):
    def __init__(self, handler: IDHandler):
        file_name, self.author_id = Util.author_info(str(input(colorstr('Enter Author(ID/Name)>? ', form=1, code=31))))
        super().__init__(handler, file_name)

    def ids(self):
        url = [f'https://www.pixiv.net/ajax/user/sef.{self.author_id}/profile/all?lang=zh']
        ids_data = Request(url, Mode.JSON)[0]['body']['illusts']
        id_list = re.findall(r"\d+", str(ids_data))
        return id_list


class ByArtworkID(IDPlugin):
    def __init__(self, handler: IDHandler):
        file_name = self.artwork_id = str(input(colorstr('Enter ArtworkID>? ', form=1, code=31)))
        super().__init__(handler, file_name)

    def ids(self):
        url = [f'https://www.pixiv.net/ajax/illust/{self.artwork_id}/recommend/init?limit={self.src_limit * 2}&lang=zh']
        artworks_data = Request(url, Mode.JSON)[0]['body']['illusts']
        id_list = sum([ids['id'] for ids in filter(lambda x: 'id' in x, artworks_data)], [])
        return id_list


class ByRanking(IDPlugin):
    def __init__(self, handler: IDHandler): super().__init__(handler, 'Ranking')

    def ids(self):
        url_list = ['https://www.pixiv.net/ranking.php?mode=daily',
                    'https://www.pixiv.net/ranking.php?mode=daily_r18']

        def get_ids(ranking_url):
            html = Request(ranking_url, Mode.HTML)[0]
            ids = re.findall('"data-type=".*?"data-id="(.*?)"', html)
            ids = [ids[i] for i in filter(lambda i: i % 2 == 0, range(len(ids)))]
            return ids
        id_list = sum([get_ids(url) for url in url_list], [])
        return id_list


class ByFollowing(IDPlugin):
    def __init__(self, handler: IDHandler): super().__init__(handler, 'Following')

    def ids(self):
        url_list = [f'https://www.pixiv.net/ajax/follow_latest/illust?p={page + 1}&mode=all&lang=zh'
                    for page in range(self.src_limit // 60 + 1)]
        id_list = sum([ids_list['body']['page']['ids'] for ids_list in Request(url_list, Mode.JSON)], [])
        return id_list


class Util:
    @staticmethod
    def author_info(author_info):
        author = {'ID': None, 'Name': None}
        if re.match(r"^\d*$", author_info) is None:
            target = 'ID'
            author_info['Name'] = author_info
            url = [f'https://www.pixiv.net/search_user.php?nick={author_info}&s_mode=s_usr']
            xpath, regex = '//h1/a[@target="_blank"][@class="title"]/@href', r'\w+/(\d+)'
        else:
            target = 'Name'
            author_info['ID'] = author_info
            url = [f'https://www.pixiv.net/users/{author_info}']
            xpath, regex = '//head/title/text()', '(.*?) - pixiv'
        try:
            result = re.findall(regex, etree.HTML(Request(url, Mode.HTML)[0]).xpath(xpath)[0])[0]
        except (IndexError, AttributeError):
            exit('Please enter correct AuthorInfo')
        author[target] = result
        return author['Name'], author['ID']
