from Main import output
from Process.Parser import *
from Process.Request import Request


class ParametricMixin(ABC):
    @staticmethod
    def shrink(id_list, _source_limit):
        _source_limit = len(id_list) if len(id_list) < _source_limit else _source_limit
        id_list = id_list[:_source_limit]
        return id_list

    @abstractmethod
    def except_id(self, param, _source_limit):
        pass

    @staticmethod
    def get_info(author_info):
        if re.match("^[0-9]*$", author_info) is not None:
            author_name = SecondINFOCaller(author_info, SecondINFOAuthorName()).Result
            author_id = author_info
        else:
            author_id = SecondINFOCaller(author_info, SecondINFOAuthorID()).Result
            author_name = author_info
        return author_name, author_id


class NonparametricMixin(ABC):
    @staticmethod
    def shrink(id_list, _source_limit):
        _source_limit = len(id_list) if len(id_list) < _source_limit else _source_limit
        id_list = id_list[:_source_limit]
        return id_list

    @abstractmethod
    def except_id(self, _source_limit):
        pass


class ExceptAuthorID(ParametricMixin):
    def except_id(self, param, _source_limit):
        author_name, author_id = self.get_info(param)
        url = [f'https://www.pixiv.net/ajax/user/{author_id}/profile/all?lang=zh']
        Request(url)
        id_list = re.findall(r"\d+", str(Request.resp_list['json'][0]['body']['illusts']))
        id_list = self.shrink(id_list, _source_limit)

        output(f'{_source_limit}', code=33, form=4, end='')
        return author_name, id_list


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
        name, new_id = ParametricPackage(ExceptAuthorID).run()
        sub_list['subscribe'].append({'author_id': author_id, 'artwork_id': new_id})
        with open('./res/subscribe.json', 'w') as f:
            f.write(json.dumps(sub_list))

    match str(input('Auto synchronize -type 1, Manual -type 2 >? ')):
        case '1':
            auto_subscribe(str(input("Enter Your Pixiv Id>? ")))
        case '2':
            write_in(str(input('Enter Author(ID/Name)>?')))


class ExceptAuthorTrace(NonparametricMixin):
    def except_id(self, _source_limit):

        id_list = []
        with open('./res/subscribe.json', 'r+') as f:
            _list = json.load(f)
        trace_list = [{
                'author_id': sub['author_id'], 'old_id': sub['artwork_id'],
                'new_ids': ExceptAuthorID().except_id(sub['author_id'], _source_limit)['id_list']
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


class ExceptRanking(NonparametricMixin):
    def except_id(self, _source_limit):
        def yield_id_list(ranking_url_list):
            html_list = Request(ranking_url_list).resp_list['html']
            for html in html_list:
                _id_list = re.findall('"data-type=".*?"data-id="(.*?)"', html)
                for i in range(1, int(len(_id_list) / 2)):
                    _id_list.pop(i)
                _id_list = self.shrink(_id_list, _source_limit)
                output(f'{len(id_list)}', code=33, form=4, end='')
                yield _id_list

        url_list = ['https://www.pixiv.net/ranking.php?mode=daily',
                    'https://www.pixiv.net/ranking.php?mode=daily_r18']
        id_list = []
        for each_id_list in yield_id_list(url_list):
            id_list += each_id_list
        return 'Ranking', id_list


class ExceptAuthorSub(NonparametricMixin):
    def except_id(self, _source_limit):
        def yield_id_list(_page_limit):
            for page in range(_page_limit):
                url = [f'https://www.pixiv.net/ajax/follow_latest/illust?p={page}&mode=all&lang=zh']
                ids = Request(url).resp_list['json'][0]['body']['page']['ids']
                yield ids

        page_limit = int(_source_limit/60)
        id_list = [ids for ids in yield_id_list(page_limit)]
        id_list = self.shrink(id_list, _source_limit)
        output(f'{len(id_list)}', code=33, form=4, end='')
        return 'Sub', id_list


class ParametricPackage:
    def __init__(self, plugin):
        self.plugin = plugin

    def run(self):
        source_limit = int(input("How many sources do you want>? "))
        param = str(input('Enter param(artworkID/author(ID/name))>? '))
        output(f'except ids({param}): ', form=1, code=31, end='')
        file_name,  id_list = self.plugin.except_id(param, source_limit)
        output(f'[finish]', form=4, code=32)
        return file_name,  id_list


class NonparametricPackage:
    def __init__(self, plugin):
        self.plugin = plugin

    def run(self):
        source_limit = int(input("How many sources do you want>? "))
        output(f'except ids: ', form=1, code=31, end='')
        file_name,  id_list = self.plugin.except_id(source_limit)
        output(f'[finish]', form=4, code=32)
        return file_name,  id_list



