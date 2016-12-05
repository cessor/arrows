(function (window) {


function Logger () {
    var self = this;
    self.records = [];

    function save () {
        // Deep Copy Records
        var records = $.extend(true, [], self.records);
        self.records = [];
        var data = {'data': records };
        $.ajax({
            url: DROPZONE_URL,
            type: 'POST',
            data: JSON.stringify(data),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            async: true
        })
        .success(function () {
            if(options.debug()) {
                console.log("Saved");
            }
        });
    }

    this.log = function (event_, data) {
        var record = {
            "event": event_,
            "data": data,
            "timestamp": new Date()
        };
        self.records.push(record);

        if(options.debug()) {
            var event_name = EVENT.find_event_name(event_);
            console.log(event_name, data, record.timestamp);
        }

        if(event_ === EVENT.VPN_CODE_END || event_ === EVENT.SAVE || event_ === EVENT.EXPERIMENT_END) {
            save();
        }
    };
}


function ParticipantCode () {
    var self = this;

    function submitCode() {
        var participantCode = $('#vpncode').val().trim();
        if (participantCode.length > 0) {
            log(EVENT.VPN_CODE_END, participantCode);
            $('#init').hide();
            self.on_done();
        }
    }

    this.open = function (on_done) {
        log(EVENT.VPN_CODE_START);
        $('#submit_code').click(submitCode);
        self.on_done = on_done;
    };
}

function Instructions () {
    var self = this;
    var pages = $('.pages p');
    pages.hide();
    pages = pages.toArray()
    var currentPage = null;

    function showNextPage () {
        if(pages.length <= 0) {
            self.close();
            return;
        }

        if(currentPage) {
            currentPage.hide();
        }

        log(EVENT.NEXT_PAGE);
        currentPage = $(pages.shift());
        currentPage.show();
    }

    this.open = function (on_done) {
        log(EVENT.INSTRUCTIONS_START);
        $('#next_instruction').click(showNextPage);
        $('#instructions').show();
        showNextPage();
        self.on_done = on_done;
    }

    this.close = function () {
        log(EVENT.INSTRUCTIONS_END);
        $('#instructions').hide();
        self.on_done();
    }
}


function TrialsLoader () {

    function Sequence (steps) {
        // Iterator over stock updates
        var self = this;
        this.steps = steps;
        this.current = -1;
        this.next = function () {
            self.current += 1;
            if (self.current >= self.steps.length) {
                return -1;
            }
            return self.steps[self.current];
        }
    }

    function extendTrial (trial) {

        trial.left = new Sequence(trial.left);
        trial.right = new Sequence(trial.right);

        function depleted (ticks) {
            return (ticks) > (this.sample_size * 2) - 1;
        }

        function showNext (ticks, ui) {
            // The ```start_with``` value contains a random bit
            // (LEFT = 0, RIGHT = 1)
            // indicating whether the left or right grid should start flashing
            // its arrows first. Ticks Mod 2 switches / alternates between the
            // left and right grid
            var direction = 0;
            if ((ticks % 2 ^ trial.start_with) == 0) {
                direction = this.left.next();
                ui.updateLeft(direction);
            } else {
                direction = this.right.next();
                ui.updateRight(direction);
            }
        }

        trial.showNext = showNext;
        trial.depleted = depleted;
        return trial;
    }

    this.loadTrials = function (callback) {
        $.get(TRIALS_URL, function (data) {
            var trials = data.trials.map(extendTrial);
            log(EVENT.TRIALS_LOADED);
            callback(trials);
        });
    }
}


function Clock (ui) {
    var start_time = null;
    var elapsed_periods = [];

    function time_elapsed_ms () {
        var now = new Date();
        return (now - start_time);
    }

    this.update = function () {
        var elapsed_percent = Math.round((time_elapsed_ms() / PERIOD) * 50) + 50 * elapsed_periods.length;
        ui.setClock(elapsed_percent);
    };

    this.start = function () {
        start_time = new Date();
        log(EVENT.CLOCK_START);
    };

    this.stop = function () {
        elapsed_periods.push([start_time, new Date()]);
        this.start_time = null;
        log(EVENT.CLOCK_STOP, elapsed_periods[elapsed_periods.length - 1]);
    }

    this.duration = function () {
        return elapsed_periods;
    }

    this.should_pause = function () {
        return (elapsed_periods.length == 0 && time_elapsed_ms() > PERIOD);
    };

    this.should_end = function () {
        return (elapsed_periods.length >= 1 && time_elapsed_ms() > PERIOD);
    };
}


function EventLoop () {
    var interval = null;
    var start = null;
    var ticks = -1;
    var callback = null;

    function tick () {
        ticks += 1;
        callback(ticks);
    }

    this.start = function (fn) {
        // Initiates the loop which calls fn
        // during each iteration. There is no delay, i.e. the program
        // runs FN immediately and then loops in the given interval.
        callback = fn;
        ticks = -1;
        start = new Date();
        tick();
        interval = setInterval(tick, TICK_INTERVAL);
    }

    this.stop = function () {
        clearInterval(interval);
        var end = new Date();
        return {
            'ticks': ticks,
            'timedelta': (end - start)
        };
    }
}


function Experiment (loader, ui, clock, eventLoop, keyboard) {

    var trials = null;
    var trial = null;

    function _renderStocks (ticks) {
        if (trial.depleted(ticks)) {
            choose();
        }
        trial.showNext(ticks, ui);
    }

    function _loadTrials (callback) {
        ui.startLoading();
        loader.loadTrials (function (data) {
            trials = data;
            ui.stopLoading();
            callback();
        });
    }

    function start () {
        log(EVENT.TRIAL_START);
        trial = trials.pop();
        ui.reset();

        keyboard
        .clear()
        .down({ 'space': run })
        .listen();
    }

    function run () {
        log(EVENT.TRIAL_RUN);
        ui.running(trial);
        eventLoop.start(_renderStocks);

        keyboard
        .clear()
        .released({'space': choose })
        .listen();
    }

    function choose () {
        log(EVENT.CHOOSE);
        var duration = eventLoop.stop();
        ui.choice();

        keyboard
        .clear()
        .released({
            'F': function () { check(LEFT, duration); },
            'J': function () { check(RIGHT, duration); }
        })
        .listen();
    }

    function check (selection, duration) {
        log(EVENT.CHECK);
        // Prevent Selection Spamming
        keyboard.clear();

        save(selection, duration);
        clock.update();

        if(clock.should_pause()) {
            pause();
            return;
        }

        if(clock.should_end()) {
            end();
            return;
        }

        _continueExperiment();
    }

    function save (selection, duration) {
        var record = jQuery.extend(trial,
            {selection: selection},
            duration
        );
        log(EVENT.SAVE, record);
    }

    function _continueExperiment () {
        if(trials.length == 0) {
            _loadTrials( start );
            return;
        }
        start();
    }

    function pause () {
        clock.stop();
        log(EVENT.PAUSE_START);
        ui.pause();

        var pauseInterval = setInterval(function () {
            clearInterval(pauseInterval);
            log(EVENT.PAUSE_END);
            clock.start();
            _continueExperiment();
        }, PAUSE);

    }

    function end () {
        // Save and Seal.
        clock.stop();
        log(EVENT.EXPERIMENT_END, clock.duration());

        // Hack. This resets your local cookie,
        // so that reloading the app actually
        // dumps the data into a new user session!
        $.get('/reset');

        ui.end();
    }

    this.start = function () {
        log(EVENT.EXPERIMENT_START);
        clock.start();
        _loadTrials(start);
    }
}


function GreenArrow () {
    var keyboard = new Keyboard({
        // If Debug is set, the keycodes in the browser will work
        // If Debug is not set, not even F5 works.
        'prevent_default': !options.debug()
    });

    var logger = new Logger();
    // Mage Globally Available;
    window.log = logger.log;

    var vpncode = new ParticipantCode();
    var instructions = new Instructions();

    var loader = new TrialsLoader();
    var eventLoop = new EventLoop();
    var ui = new ExperimentUI();
    var clock = new Clock(ui);
    var experiment = new Experiment(loader, ui, clock, eventLoop, keyboard);

    function start () {
        ui.stopLoading();

        vpncode.open(function () {
            instructions.open(experiment.start);
        });

        if(options.debug() && options.experiment()) {
            instructions.close();
        }

    }
    log(EVENT.APPLICATION_START);
    start();
}

window.application = new GreenArrow();

})(window);
