import re
from abc import abstractmethod

from lxml import etree

from PixivCrawler.Crawler.SemiCrawler.IDHandler import ICrawler, IDHandler
from ...Util.Requests.Proxy import Download


def colour_str(message, code, form=0):
    return f'\033[{form};{code}m{message}\033[0m'


class IDCaptor(ICrawler):
    source_limit = 0

    def __init__(self, handler):
        if not isinstance(handler, IDHandler):
            raise TypeError
        self.Handler = handler

    def crawl(self):
        file_name, id_list = self.decor()
        self.source_limit = len(id_list) if len(id_list) < self.source_limit else self.source_limit
        id_list = id_list[:self.source_limit]
        self.Handler.file_name, self.Handler.id_list = file_name, id_list
        self.Handler.crawl()

    @abstractmethod
    def decor(self) -> (str, []):
        pass


class ByAuthorID(IDCaptor):
    def __init__(self, crawler):
        super().__init__(crawler)
        self.author_info = str(input(colour_str('Enter Author(ID/Name)>? ', form=1, code=31)))

    def decor(self):
        author_name, author_id = Util.get_author_info(self.author_info)
        url = [f'https://www.pixiv.net/ajax/user/{author_id}/profile/all?lang=zh']
        ids_data = Download.response(url)['json'][0]['body']['illusts']
        id_list = re.findall(r"\d+", str(ids_data))
        return author_name, id_list


class ByArtworkID(IDCaptor):
    def __init__(self, crawler):
        super().__init__(crawler)
        self.artwork_id = str(input(colour_str('Enter ArtworkID>? ', form=1, code=31)))

    def decor(self):
        url = [f'https://www.pixiv.net/ajax/illust/{self.artwork_id}/recommend/init?limit={self.source_limit * 2}&lang=zh']
        artworks_data = Download.response(url)['json'][0]['body']['illusts']
        id_list = []
        for artwork in artworks_data:
            if 'id' in artwork:
                id_list.append(artwork['id'])
        return self.artwork_id, id_list


class ByRanking(IDCaptor):
    def decor(self):
        def yield_id_list(ranking_url_list):
            for html in Download.response(ranking_url_list)['html']:
                _id_list = re.findall('"data-type=".*?"data-id="(.*?)"', html)
                _id_list = _id_list[:int(self.source_limit)]
                for i in range(1, int(len(_id_list) / 2)):
                    _id_list.pop(i)
                yield _id_list

        url_list = ['https://www.pixiv.net/ranking.php?mode=daily',
                    'https://www.pixiv.net/ranking.php?mode=daily_r18']
        id_list = []
        for each_id_list in yield_id_list(url_list):
            id_list += each_id_list
        return 'Ranking', id_list


class BySub(IDCaptor):
    def decor(self):
        id_list = []
        page_limit = int(self.source_limit / 60) + 1
        url_list = [f'https://www.pixiv.net/ajax/follow_latest/illust?p={page}&mode=all&lang=zh'
                    for page in range(1, page_limit + 1)]
        for ids_list in Download.response(url_list)['json']:
            id_list += ids_list['body']['page']['ids']
        return 'Sub', id_list


class Util:
    @staticmethod
    def get_author_info(author_info):
        if re.match("^[0-9]*$", author_info) is not None:
            try:
                url = [f'https://www.pixiv.net/users/{author_info}']
                html = Download.response(url)['html'][0]
                name_data = etree.HTML(html).xpath('//head/title/text()')[0]
                author_name = re.findall('(.*?) - pixiv', name_data)[0]
            except (IndexError, AttributeError):
                print(colour_str('Please enter correct AuthorID ', form=1, code=31))
                exit()
            author_id = author_info
        else:
            try:
                url = [f'https://www.pixiv.net/search_user.php?nick={author_info}&s_mode=s_usr']
                html = Download.response(url)['html'][0]
                id_data = etree.HTML(html).xpath('//h1/a[@target="_blank"][@class="title"]/@href')[0]
                author_id = re.findall(r'\w+/(\d+)', id_data)[0]
            except (IndexError, AttributeError):
                print(colour_str('Please enter correct AuthorName ', form=1, code=31))
                exit()
            author_name = author_info
        return author_name, author_id


