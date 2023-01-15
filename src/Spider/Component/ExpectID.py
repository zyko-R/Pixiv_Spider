from abc import abstractmethod
import re
from lxml import etree
import json
from Downloader import Request
from Spider.Component.Prototype import Crawler


def output(message, code, form=0, end='\n'):
    print(f'\033[{form};{code}m{message}\033[0m', end=end)


class CrawlerExceptIDDecorator(Crawler):
    decorated_crawler = None

    def __init__(self, crawler):
        self.decorated_crawler = crawler
        self.source_limit = int(input('How many src do you want>? '))

    def crawl(self):
        self.decorated_crawler.file_name, self.decorated_crawler.id_list = self.except_id()
        self.decorated_crawler.id_list = self.shrink(self.decorated_crawler.id_list, self.source_limit)
        self.decorated_crawler.crawl()

    @abstractmethod
    def except_id(self) -> (str, []):
        pass

    @staticmethod
    def shrink(id_list, _source_limit):
        _source_limit = len(id_list) if len(id_list) < _source_limit else _source_limit
        id_list = id_list[:_source_limit]
        return id_list


class ByAuthorID(CrawlerExceptIDDecorator):
    def __init__(self, crawler):
        super().__init__(crawler)
        self.author_info = str(input('Enter Author(ID/Name)>? '))

    def except_id(self):
        author_name, author_id = Util.get_info(self.author_info)
        url = [f'https://www.pixiv.net/ajax/user/{author_id}/profile/all?lang=zh']
        Request(url)
        id_list = re.findall(r"\d+", str(Request.resp_list['json'][0]['body']['illusts']))
        return author_name, id_list


class ByArtworkID(CrawlerExceptIDDecorator):
    def __init__(self, crawler):
        super().__init__(crawler)
        self.source_limit *= 2
        self.artwork_id = str(input('Enter ArtworkID>? '))

    def except_id(self):
        url = [f'https://www.pixiv.net/ajax/illust/{self.artwork_id}/recommend/init?limit={self.source_limit}&lang=zh']
        artwork__list = Request(url).resp_list['json'][0]['body']['illusts']
        id_list = []
        for artwork in artwork__list:
            if 'id' in artwork:
                id_list.append(artwork['id'])
        return self.artwork_id, id_list


class ByTrace(CrawlerExceptIDDecorator):
    def __init__(self, crawler):
        super().__init__(crawler)

    def except_id(self):
        def artwork_except(artwork_id, source_limit):
            url = [
                f'https://www.pixiv.net/ajax/illust/{artwork_id}/recommend/init?limit={source_limit}&lang=zh']
            Request(url)
            author_artwork_id_list = re.findall(r"\d+", str(Request.resp_list['json'][0]['body']['illusts']))
            return author_artwork_id_list

        id_list = []
        with open('./res/subscribe.json', 'r+') as f:
            _list = json.load(f)
        trace_list = [{
                'author_id': sub['author_id'], 'old_id': sub['artwork_id'],
                'new_ids': artwork_except(sub['artwork_id'], self.source_limit)
             } for sub in _list['subscribe']
        ]

        def yield_pending_ids(_trace_list):
            _pending_id_list = []
            for _trace in _trace_list:
                for new_id in _trace['new_ids']:
                    if new_id == _trace['old_id']:
                        break
                    _pending_id_list.append(new_id)
                _author_id = _trace['author_id']
                yield _author_id, _pending_id_list

        update_list = []
        for author_id, pending_id_list in yield_pending_ids(trace_list):
            if len(pending_id_list) != 0:
                id_list += pending_id_list
                update_list.append({'author_id': author_id, 'id': pending_id_list[0]})

        for update in update_list:
            for sub in _list['subscribe']:
                if sub['author_id'] == update['author_id']:
                    sub['artwork_id'] = update['id']
                    break
        with open('./res/subscribe.json', 'w+') as f:
            f.write(json.dumps(_list))
        return 'Update', id_list


class ByRanking(CrawlerExceptIDDecorator):
    def __init__(self, crawler):
        super().__init__(crawler)
        self.source_limit /= 2

    def except_id(self):
        def yield_id_list(ranking_url_list):
            html_list = Request(ranking_url_list).resp_list['html']
            for html in html_list:
                _id_list = re.findall('"data-type=".*?"data-id="(.*?)"', html)
                for i in range(1, int(len(_id_list) / 2)):
                    _id_list.pop(i)
                yield _id_list

        url_list = ['https://www.pixiv.net/ranking.php?mode=daily',
                    'https://www.pixiv.net/ranking.php?mode=daily_r18']
        id_list = []
        for each_id_list in yield_id_list(url_list):
            id_list += each_id_list
        return 'Ranking', id_list


class BySub(CrawlerExceptIDDecorator):
    def __init__(self, crawler):
        super().__init__(crawler)

    def except_id(self):
        def yield_id_list(_page_limit):
            for page in range(_page_limit):
                url = [f'https://www.pixiv.net/ajax/follow_latest/illust?p={page}&mode=all&lang=zh']
                ids = Request(url).resp_list['json'][0]['body']['page']['ids']
                yield ids

        page_limit = int(self.source_limit/60)
        id_list = [ids for ids in yield_id_list(page_limit)]
        return 'Sub', id_list


class Util:
    @staticmethod
    def get_info(author_info):
        if re.match("^[0-9]*$", author_info) is not None:
            try:
                url = [f'https://www.pixiv.net/users/{author_info}']
                Request(url)
                html = Request.resp_list['html'][0]
                name_data = etree.HTML(html).xpath('//head/title/text()')[0]
                author_name = re.findall('(.*?) - pixiv', name_data)[0]
            except IndexError:
                output('Please enter correct AuthorID', code=31, form=1)
                exit()
            author_id = author_info
        else:
            try:
                url = [f'https://www.pixiv.net/search_user.php?nick={author_info}&s_mode=s_usr']
                Request(url)
                html = Request.resp_list['html'][0]
                id_data = etree.HTML(html).xpath('//h1/a[@target="_blank"][@class="title"]/@href')[0]
                author_id = re.findall(r'\w+/(\d+)', id_data)[0]
            except IndexError:
                output('Please enter correct AuthorName', code=31, form=1)
                exit()
            author_name = author_info
        return author_name, author_id

    @staticmethod
    def subscribe():

        def auto_subscribe(user_id):
            url = [f'https://www.pixiv.net/ajax/user/{user_id}'
                   f'/following?offset=0&limit=100&rest=show&tag=&acceptingRequests=0&lang=zh']
            user_list = Request(url).resp_list['json'][0]
            for user in user_list['body']['users']:
                write_in(user['userId'])

        def write_in(author_id):
            sub_list = {'subscribe': []}
            try:
                with open('./res/subscribe.json', 'r+') as f:
                    sub_list = json.load(f)
            except (TypeError, json.decoder.JSONDecodeError):
                pass
            for sub in sub_list['subscribe']:
                if author_id == sub['author_id']:
                    return

            def expect_id():
                author_name, _ = Util.get_info(author_id)
                url = [f'https://www.pixiv.net/ajax/user/{author_id}/profile/all?lang=zh']
                id_data = Request(url).resp_list['json'][0]['body']['illusts']
                id_list = re.findall(r"\d+", str(id_data))
                return author_name, id_list[0]

            name, new_id = expect_id()
            sub_list['subscribe'].append({'author_id': author_id, 'artwork_id': new_id})
            with open('./res/subscribe.json', 'w') as f:
                f.write(json.dumps(sub_list))

        match str(input('Auto synchronize -type 1, Manual -type 2 >? ')):
            case '1':
                auto_subscribe(str(input("Enter Your Pixiv Id>? ")))
            case '2':
                write_in(str(input('Enter Author(ID/Name)>?')))
