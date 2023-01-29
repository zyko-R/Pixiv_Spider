import re
from abc import abstractmethod

from lxml import etree

from PixivCrawler.Crawler.Prototype.IDHandler import ICrawler, IDHandler
from PixivCrawler.Downloader.PluginsXProxy import Download


def colorstr(message, code, form=0):
    return f'\033[{form};{code}m{message}\033[0m'


class IDPlugin(ICrawler):
    src_limit = 0

    def __init__(self, handler: IDHandler, file_name: str):
        self.Handler, self.file_name = handler, file_name

    def crawl(self, file_name: None = None, id_list: None = None):
        id_list = self.decor()
        print(colorstr(f'GettingID<{len(id_list)}>[Finish]', form=1, code=34))
        id_list = id_list[:len(id_list) if len(id_list) < self.src_limit else self.src_limit]
        self.Handler.crawl(self.file_name, id_list)

    @abstractmethod
    def decor(self) -> []: pass


class ByAuthorID(IDPlugin):
    def __init__(self, handler: IDHandler):
        author_info = str(input(colorstr('Enter Author(ID/Name)>? ', form=1, code=31)))
        author_name, self.author_id = Util.get_author_info(author_info)
        super().__init__(handler, file_name=author_name)

    def decor(self):
        url = [f'https://www.pixiv.net/ajax/user/{self.author_id}/profile/all?lang=zh']
        ids_data = Download.response(url)['json'][0]['body']['illusts']
        id_list = re.findall(r"\d+", str(ids_data))
        return id_list


class ByArtworkID(IDPlugin):
    def __init__(self, handler: IDHandler):
        self.artwork_id = str(input(colorstr('Enter ArtworkID>? ', form=1, code=31)))
        super().__init__(handler, file_name=self.artwork_id)

    def decor(self):
        url = [f'https://www.pixiv.net/ajax/illust/{self.artwork_id}/recommend/init?limit={self.src_limit * 2}&lang=zh']
        artworks_data = Download.response(url)['json'][0]['body']['illusts']
        id_list = sum([ids['id'] for ids in filter(lambda x: 'id' in x, artworks_data)], [])
        return id_list


class ByRanking(IDPlugin):
    def __init__(self, handler: IDHandler):
        super().__init__(handler, file_name='Ranking')

    def decor(self):
        url_list = ['https://www.pixiv.net/ranking.php?mode=daily',
                    'https://www.pixiv.net/ranking.php?mode=daily_r18']

        def get_ids(ranking_url):
            html = Download.response([ranking_url])['html'][0]
            ids = re.findall('"data-type=".*?"data-id="(.*?)"', html)
            ids = [ids[i] for i in filter(lambda i: i % 2 == 0, range(len(ids)))]
            return ids
        id_list = sum([get_ids(url) for url in url_list], [])
        return id_list


class ByFollowing(IDPlugin):
    def __init__(self, handler: IDHandler):
        super().__init__(handler, file_name='Following')

    def decor(self):
        url_list = [f'https://www.pixiv.net/ajax/follow_latest/illust?p={page + 1}&mode=all&lang=zh'
                    for page in range(int(self.src_limit / 60) + 1)]
        id_list = sum([ids_list['body']['page']['ids'] for ids_list in Download.response(url_list)['json']], [])
        return id_list


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
                print(colorstr('Please enter correct AuthorID ', form=1, code=31))
                exit()
            author_id = author_info
        else:
            try:
                url = [f'https://www.pixiv.net/search_user.php?nick={author_info}&s_mode=s_usr']
                html = Download.response(url)['html'][0]
                id_data = etree.HTML(html).xpath('//h1/a[@target="_blank"][@class="title"]/@href')[0]
                author_id = re.findall(r'\w+/(\d+)', id_data)[0]
            except (IndexError, AttributeError):
                print(colorstr('Please enter correct AuthorName ', form=1, code=31))
                exit()
            author_name = author_info
        return author_name, author_id
