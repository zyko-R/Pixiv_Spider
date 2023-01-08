from Process.Request import Request
from Spider.Prototype import *
from Spider.plugins import *


class CrawlerMixin(ABC):
    @staticmethod
    def clone_crawler():
        return Crawler

    @staticmethod
    def get_info(author_info):
        if re.match("^[0-9]*$", author_info) is not None:
            author_name = SecondINFOCaller(author_info, SecondINFOAuthorName()).Result
            author_id = author_info
        else:
            author_id = SecondINFOCaller(author_info, SecondINFOAuthorID()).Result
            author_name = author_info
        return author_name, author_id


class FocusedAuthorCrawler(CrawlerMixin):
    def __init__(self, param, _source_limit):
        author_name, author_id = self.get_info(param)
        id_list = FocusedExceptCaller(param, _source_limit, ExceptAuthorID()).Result['id_list']
        self.clone_crawler()(id_list, author_name).work()


class AuthorTraceCrawler(CrawlerMixin):
    def __init__(self, _source_limit):
        author_id_list = IncrementExceptCaller(_source_limit, ExceptAuthorSub()).Result
        for author_id in author_id_list:
            author_name, author_id = self.get_info(author_id)
            self.clone_crawler()(author_id['id_list'], author_name).work()

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
                if sub['author_id'] == author_id:
                    return
            else:
                new_id = FocusedExceptCaller(author_id, 1, ExceptAuthorID()).Result['id_list'][0]
                sub_list['subscribe'].append({'author_id': author_id, 'artwork_id': new_id})
            with open('./res/subscribe.json', 'w') as f:
                f.write(json.dumps(sub_list))

        match str(input('Auto synchronize -type 1, Manual -type 2')):
            case '1':
                auto_subscribe(str(input("Enter Your Pixiv Id>? ")))
            case '2':
                write_in(str(input('Enter Author(ID/Name)>?')))


class SubArtworkCrawler(CrawlerMixin):
    def __init__(self, _source_limit):
        id_list = IncrementExceptCaller(_source_limit, ExceptAuthorSub()).Result
        self.clone_crawler()(id_list, 'SubArtwork').work()


class RankingCrawler(CrawlerMixin):
    def __init__(self, _source_limit):
        id_list = IncrementExceptCaller(_source_limit, ExceptRanking()).Result
        self.clone_crawler()(id_list, 'Ranking').work()
