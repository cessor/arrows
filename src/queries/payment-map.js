
/*
  Filters each Participant's trials for saved trial data and
  evaluates whether the participant selected the better stock

  Try with:

    db.out.remove({})
    db.participants.mapReduce(map, reduce, {out: 'out'});
    db.out.find()
*/
//Calculate Payments:
function () {
  function correct(p1, p2, selection) {
    // Selection is either LEFT (0) or RIGHT (1)
    // If the left stock was better than the right, the
    // participant chose correctly if he selected left an so on.
    return ([p1 > p2, p1 < p2][selection] ? 1 : 0);
  }

  var self = this;
  var SAVE_DATA_EVENT = 5;

  function emit_correct_choices (trial) {
    if(trial.event != SAVE_DATA_EVENT) {
      return;
    }

    var data = trial.data;
    if(!data){
      return;
    }

    var choice_was_correct = correct(
        data.empirical_p1,
        data.empirical_p2,
        data.selection
    );

    var key = {
      '_id': self._id,
      'tag': self.tag || self.PARTICIPANT_ID,
      'PARTICIPANT_ID': self.PARTICIPANT_ID
    };
    emit(key, choice_was_correct);
  }

  if(!this.trials) {
    return;
  }

  this.trials.forEach(emit_correct_choices);
};
