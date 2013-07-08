from mongows.mws.db import get_db
from mongows.mws.util import UseResId
from abc import ABCMeta, abstractmethod
from collections import Counter


class ValidationTest:
    __metaclass__ = ABCMeta

    def __init__(self, res_id):
        self.res_id = res_id
        self.db = get_db()

    def __hashDict(self, d):
        for key in d:
            if isinstance(d[key], dict):
                d[key] = __hashDict(d[key])
        return tuple(d.items())

    # Collection must exactly equal the data set
    def collection_equals(self, collection, data):
        data = [self.__hashDict(x) for x in data]
        with UseResId(self.res_id):
            result = list(self.db[collection].find({}, {'_id': 0}))
            result = [self.__hashDict(x) for x in result]
            return Counter(result) == Counter(data)

    # Data must be a subset of collection
    def collection_contains(self, collection, data):
        with UseResId(self.res_id):
            result = list(self.db[collection].find({'$or': data}, {'_id': 0}))
            return all(x in result for x in data)

    # Collection must contain one or more of the elements in data
    def collection_contains_any(self, collection, data):
        with UseResId(self.res_id):
            result = list(self.db[collection].find({'$or': data}, {'_id': 0}))
            return any(x in result for x in data)

    # Collection does not contain any of the elements in data
    def collection_contains_none(self, collection, data):
        return not self.collection_contains_any(collection, data)

    # Require all inheriting classes to implement a run method
    @abstractmethod
    def run(self):
        pass
