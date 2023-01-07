import json
from abc import ABC, abstractmethod
import re
from Main import output
from Request import Request


class ExceptMixin(ABC):
    @staticmethod
    def shrink(id_list, _source_limit):
        _source_limit = len(id_list) if len(id_list) < _source_limit else _source_limit
        id_list = id_list[:_source_limit]
        return id_list

    @abstractmethod
    def except_id(self, param, _source_limit):
        pass


class ExceptAuthor_ID(ExceptMixin):
    def except_id(self, param, _source_limit):
        url = [f'https://www.pixiv.net/ajax/user/{param}/profile/all?lang=zh']
        Request(url)
        id_list = re.findall(r"\d+", str(Request.resp_list['json'][0]['body']['illusts']))
        id_list = self.shrink(id_list, _source_limit)

        output(f'{_source_limit}', code=33, form=4, end='')
        return {'author id': param, 'id_list': id_list}


class ExceptCaller:
    Result = []

    @classmethod
    def __init__(cls, param, _source_limit, except_mixin):
        cls.Result = []
        output(f'except ids({param}): ', form=1, code=31, end='')
        cls.Result = except_mixin.except_id(param, _source_limit)
        output(f'[finish]', form=4, code=32)


class Increment(ABC):
    @abstractmethod
    def except_id(self, _source_limit):
        pass


class AuthorSub(Increment):
    @staticmethod
    def subscribe(author_id):
        _list = {'subscribe': []}
        try:
            with open('./res/subscribe.json', 'r+') as f:
                _list = json.dumps(f)
        except (TypeError, json.decoder.JSONDecodeError):
            pass
        finally:
            new_id = ExceptCaller(author_id, 1, ExceptAuthor_ID()).Result['id_list'][0]
            _list['subscribe'].append({'author_id': author_id, 'artwork_id': new_id})
            with open('./res/subscribe.json', 'w+') as f:
                f.write(json.dumps(_list))

    def except_id(self, _source_limit):
        id_author_list = []
        with open('./res/subscribe.json', 'r+') as f:
            _list = json.load(f)
        # sub_list = [{'author id':sub['author id'],'artwork id':sub['artwork id']}for sub in _list['subscribe_list']]
        sub_list = _list['subscribe']
        pending_list = []
        for sub in sub_list:
            new_ids = ExceptCaller(sub['author_id'], _source_limit, ExceptAuthor_ID()).Result['id_list']
            pending_list.append({'author_id': sub['author_id'], 'old_id': sub['artwork_id'], 'new_ids': new_ids})

        for pending in pending_list:
            id_list = []
            for new_id in pending['new_ids']:
                if new_id == pending['old_id']:
                    break
                else:
                    id_list.append(new_id)
            if len(id_list) != 0:
                for sub in _list['subscribe']:
                    if sub['author_id'] == pending['author_id']:
                        sub['artwork_id'] = pending['new_ids'][0]
                        break
                id_author_list.append({'author_id': pending['author_id'], 'id_list': id_list})

        with open('./res/subscribe.json', 'w+') as f:
            f.write(json.dumps(_list))

        return id_author_list
