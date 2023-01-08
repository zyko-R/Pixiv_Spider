import json
from abc import ABC, abstractmethod
import re
from Main import output
from Process.Request import Request


class FocusedMixin(ABC):
    @staticmethod
    def shrink(id_list, _source_limit):
        _source_limit = len(id_list) if len(id_list) < _source_limit else _source_limit
        id_list = id_list[:_source_limit]
        return id_list

    @abstractmethod
    def except_id(self, param, _source_limit):
        pass


class ExceptAuthorID(FocusedMixin):
    def except_id(self, param, _source_limit):
        url = [f'https://www.pixiv.net/ajax/user/{param}/profile/all?lang=zh']
        Request(url)
        id_list = re.findall(r"\d+", str(Request.resp_list['json'][0]['body']['illusts']))
        id_list = self.shrink(id_list, _source_limit)

        output(f'{_source_limit}', code=33, form=4, end='')
        return {'author id': param, 'id_list': id_list}


class FocusedExceptCaller:
    Result = []

    @classmethod
    def __init__(cls, param, _source_limit, except_mixin):
        cls.Result = []
        output(f'except ids({param}): ', form=1, code=31, end='')
        cls.Result = except_mixin.except_id(param, _source_limit)
        output(f'[finish]', form=4, code=32)


class IncrementMixin(ABC):
    @abstractmethod
    def except_id(self, _source_limit):
        pass


class ExceptAuthorSub(IncrementMixin):
    @staticmethod
    def subscribe(author_id):
        sub_list = {'subscribe': []}
        try:
            with open('./res/subscribe.json', 'r+') as f:
                sub_list = json.load(f)

        except (TypeError, json.decoder.JSONDecodeError):
            pass
        for sub in sub_list['subscribe']:
            if sub['author_id'] == author_id:
                exit('you have already followed him/her')
        else:
            new_id = FocusedExceptCaller(author_id, 1, ExceptAuthorID()).Result['id_list'][0]
            sub_list['subscribe'].append({'author_id': author_id, 'artwork_id': new_id})
        with open('./res/subscribe.json', 'w') as f:
            f.write(json.dumps(sub_list))

    def except_id(self, _source_limit):
        update_list = []
        with open('./res/subscribe.json', 'r+') as f:
            _list = json.load(f)
        pending_list = [{
                'author_id': sub['author_id'], 'old_id': sub['artwork_id'],
                'new_ids': FocusedExceptCaller(sub['author_id'], _source_limit, ExceptAuthorID()).Result['id_list']
             } for sub in _list['subscribe']
        ]
        for pending in pending_list:
            id_list = []
            for new_id in pending['new_ids']:
                if new_id == pending['old_id']:
                    break
                id_list.append(new_id)
            if len(id_list) != 0:
                update_list.append({'author_id': pending['author_id'], 'id_list': id_list})
        for update in update_list:
            for sub in _list['subscribe']:
                if sub['author_id'] == update['author_id']:
                    sub['artwork_id'] = update['id_list'][0]
                    break
        with open('./res/subscribe.json', 'w+') as f:
            f.write(json.dumps(_list))
        return update_list


class ExceptRanking(IncrementMixin):
    def except_id(self, _source_limit):
        url = ['https://www.pixiv.net/ranking.php?mode=daily']
        match str(input('if you want r18s, please type 1>? ')):
            case '1': url[0] += '_r18'
        html = Request(url).resp_list['html'][0]
        id_list = re.findall('"data-type=".*?"data-id="(.*?)"', html)
        for i in range(1, int(len(id_list)/2)):
            id_list.pop(i)
        id_list = id_list[:_source_limit]
        output(f'{len(id_list)}', code=33, form=4, end='')
        return id_list


class IncrementExceptCaller:
    Result = []

    @classmethod
    def __init__(cls, _source_limit, except_mixin):
        cls.Result = []
        output(f'except ids: ', form=1, code=31, end='')
        cls.Result = except_mixin.except_id(_source_limit)
        output(f'[finish]', form=4, code=32)



