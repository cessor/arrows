function (key, values) {
    var correct_trials = Array.sum(values);
    var total_trials = values.length;
    var incorrect_trials = total_trials - correct_trials;
    return {
        correct_trials: correct_trials,
        total_trials: total_trials,
        incorrect_trials: incorrect_trials
    };
};
