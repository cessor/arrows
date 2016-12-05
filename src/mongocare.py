__all__ = [
    'ID', 'ID_KEY', 'Is', 'and_', 'both', 'by',
    'by_id', 'combine', 'contains', 'document',
    'does_not_contain', 'isotimestamp',
    'in_', 'increment', 'inc', 'mark', 'nin', 'not_in',
    'equals', 'exists', 'get', 'increment', 'set_',
    'not_exists', 'ObjectDict', 'or_', 'parse_iso_datetime', 'push', 'pk', 'update'

    ,'match', 'project', 'size'
]

from datetime import datetime
from bson.objectid import ObjectId
from pymongo.son_manipulator import SONManipulator

ID_KEY = _id = ID = '_id'


class ObjectIdAsTimestamp(SONManipulator):
    def transform_outgoing(self, son, collection):
        _id = son.get(ID_KEY, None)
        if not _id:
            return son
        son['_timestamp'] = _id.generation_time.isoformat()
        son[ID_KEY] = str(_id)
        return son


class ObjectDict(dict):
    """Makes a dictionary behave like an object, with attribute-style access.
    """
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value


def parse_iso_datetime(iso_string):
    iso_string_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    return datetime.strptime(iso_string, iso_string_format)


def and_(a, b):
    '''A convenient $and operator for mongodb queries'''
    return document('$and', [a, b])
both = and_


# Find By ID
def by(key):
    '''A convenient find by shortcut, so that you can do for example:
        db.col.find(by(ID))
    '''
    return document(_id, key)


def by_id(key):
    ''' Wraps the given value in an object id'''
    return document(_id, ObjectId(key))


def contains(fieldname, array):
    '''A convenient $in operator for mongodb queries'''
    return document(fieldname, {'$in': array})
in_ = contains


def combine(*docs):
    d = {}
    for doc in docs:
        d.update(doc)
    return d


def document(fieldname, value):
    '''Creates a document'''
    d = {}
    d[str(fieldname)] = value
    return d


def equals(fieldname, value):
    return document(fieldname, {'$eq': value})


def does_not_contain(fieldname, array):
    return document(fieldname, {'$nin': array})
not_in = nin = does_not_contain


def exists(fieldname):
    '''A convenient $exists operator for mongodb queries'''
    return document(fieldname, {'$exists': True})


def increment(fieldname):
    '''A convenient $inc operator for mongodb queries'''
    return {"$inc": document(fieldname, 1)}
inc = increment


def isotimestamp(fieldname):
    return document(fieldname, datetime.utcnow().isoformat())


def mark(doc):
    doc.update(isotimestamp('created'))
    return doc


def match(doc):
    '''A convenient $match operator for mongodb aggregate queries'''
    return document('$match', doc)


def not_exists(fieldname):
    '''A convenient negated $exists operator for mongodb queries'''
    return document(fieldname, {'$exists': False})


def or_(a, b):
    '''A convenient $or operator for mongodb queries'''
    return document('$or', [a, b])
either = or_


def push(fieldname, value):
    return {'$push': document(fieldname, value)}


def project(doc):
    '''A convenient $project operator for mongodb aggregate queries'''
    return document('$project', doc)


def size(fieldname):
    '''A convenient $size operator for mongodb aggregate queries'''
    return document(fieldname, {'$size': '$%s' % fieldname})


def update(fieldname, value):
    return {'$set': document(fieldname, value)}
set_ = update


# Query: Is(False).Field
class Is(object):
    '''A convenient equals operator for mongodb queries.
    It allows you to write.:
        db.col.find(Is(True).fieldname)
    '''
    def __init__(self, value):
        self.value = value

    def __getattr__(self, name):
        return equals(name, self.value)


def _get(fieldname):
    return {str(fieldname): True}


# Projection
class Get(object):
    def __call__(self, fieldname):
        return _get(fieldname)

    def __getattr__(self, fieldname):
        return _get(fieldname)


# Allows get.field
get = Get()

# Projection
pk = get(_id)
