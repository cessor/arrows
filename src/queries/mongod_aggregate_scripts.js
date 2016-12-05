db.participants.aggregate([
  {$unwind: '$trials'},
  {$match: {'trials.event':  {$gte: 1000}}},
  {$project: {tag: 1, PARTICIPANT_ID: 1, trials: 1}},
  {$group: {
    _id: {
      _id: '$_id',
      participant_id: '$PARTICIPANT_ID',
      tag: '$tag'
    },
    events: { $push: '$trials' }
  }}
])
