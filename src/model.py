from bson.objectid import ObjectId
import uuid

SESSIONS_COLLECTION = 'participants'
MAP_FUNCTION_FILE = 'queries/payment-map.js'
REDUCE_FUNCTION_FILE = 'queries/payment-reduce.js'

class Participant(object):
    KEY = 'PARTICIPANT_ID'
    def __init__(self):
        self.session_id = uuid.uuid4().hex

    def document(self):
        document_ = {}
        document_[self.KEY] = self.session_id
        return document_


class Participants(object):
    def __init__(self, db):
        self.collection = db[SESSIONS_COLLECTION]
        with open(MAP_FUNCTION_FILE, 'r') as map_file:
            self.map_js = map_file.read()
        with open(REDUCE_FUNCTION_FILE, 'r') as reduce_file:
            self.reduce_js = reduce_file.read()

    def create(self, participant):
        return self.collection.insert(participant.document())

    def add_trials(self, participant_id, trials):
        return self.collection.update(
            {Participant.KEY: participant_id},
            {'$push': {'trials': {'$each': trials}}},
            upsert=True
        )

    def update_tag(self, participant_id, tag):
        print(participant_id)
        return self.collection.update(
            {Participant.KEY: participant_id},
            {'$set': {'tag': tag }}
        )

    def all(self):
        return self.collection.inline_map_reduce(self.map_js, self.reduce_js)

    def one(self, participant_id):
        return self.collection.find_one({
            Participant.KEY: participant_id
        })

    def get_all_events(self):
        return self.collection.aggregate([
            {'$unwind': '$trials'},
            {'$match': {'trials.event': 5}},
            {'$project': {
                "participant_id": "$PARTICIPANT_ID",
                "tag": "$tag",
                "timestamp" : "$trials.timestamp",
                "delta": "$trials.data.delta",
                "p1": "$trials.data.p1",
                "p2": "$trials.data.p2",
                "subrange_key": "$trials.data.subrange_key",
                "empirical_delta": "$trials.data.empirical_delta",
                "empirical_p1": "$trials.data.empirical_p1",
                "empirical_p2": "$trials.data.empirical_p2",
                "sample_size": "$trials.data.sample_size",
                "selection": "$trials.data.selection",
                "start_with": "$trials.data.start_with",
                "ticks": "$trials.data.ticks",
                "timedelta": "$trials.data.timedelta",
                "last_left": "$trials.data.left.current",
                "last_right": "$trials.data.right.current",
                "left": "$trials.data.left.steps",
                "right": "$trials.data.right.steps",
            }}])
