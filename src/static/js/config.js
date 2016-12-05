// Constants
var LEFT = 0;
var RIGHT = 1;

// Arrows (Used for displaying and Preloading)
var arrows = {};
var UP = 1;
var DOWN = 0;
var ARROW_UP = 'static/img/up.svg';
var ARROW_DOWN = 'static/img/down.svg';
arrows[UP] = ARROW_UP;
arrows[DOWN] = ARROW_DOWN;
var ARROW_PADDING = 4;

// Trial data is being loaded from here.
var TRIALS_URL = '/api/trials';

// Data is stored here.
var DROPZONE_URL = '/api/data';

// UI Element Labels
var BUTTON_START = "Leertaste halten";
var BUTTON_STOP = "Loslassen um anzuhalten";
var HINT_DECISION = "Drücken Sie F für Wertpapier A. Drücken Sie J für Wertpapier B."
var HINT_START = "Halten sie die Leertaste gedrückt. Loslassen der Leertaste beendet den Durchgang";

// Grid Config: 6x6 Cells
var GRID_ROWS = 6;
var GRID_COLUMNS = GRID_ROWS;

// Every Half Second
var TICK_INTERVAL = 500;

// The duration of the PAUSE phase in Milliseconds
var PAUSE = 2 * 60 * 1000;

// The duration of each period (the time during which participants see stock updates)
var PERIOD = 13 * 60 * 1000;


// Event IDs
var EVENT = {
    APPLICATION_START: 1000,
    INSTRUCTIONS_START: 1001,
    NEXT_PAGE: 1002,
    INSTRUCTIONS_END: 1003,
    EXPERIMENT_START: 1004,
    CLOCK_START: 1005,
    CLOCK_STOP: 1006,
    TRIALS_LOADED: 1007,
    PAUSE_START: 1008,
    PAUSE_END: 1009,
    EXPERIMENT_END: 1010,
    TRIAL_START: 1,
    TRIAL_RUN: 2,
    CHOOSE: 3,
    CHECK: 4,
    SAVE: 5,
    VPN_CODE_START: 1020,
    VPN_CODE_END: 1021
};


(function setup (window) {
function Options () {
    var keys = [
        'debug', 'experiment', 'fast', 'short'
    ];

    var hash = window.location.hash;

    function find(key) {
        return function () {
            return (hash.indexOf(key) > -1);
        }
    }

    // Register Keys
    var len = keys.length;
    for(var i = 0; i < len; i++) {
        var key = keys[i];
        this[key] = find(key);
    }
}
window.options = new Options();

if (options.debug() && options.fast()) {
    // To test the timing and flow, add #debug-fast to the url
    // in order to make the app run really fast.
    TICK_INTERVAL = 50;
    PERIOD = 5 * 1000;
    PAUSE = 5 * 1000;
}

if (options.debug() && options.short()) {
    // To test the timing and flow, add #debug-fast to the url
    // in order to make the app run really fast.
    TICK_INTERVAL = 500;
    PERIOD = 2 * 60 * 1000;
    PAUSE = 10 * 1000;
}

(function setupReverseEventLookup () {
    var code_map = {};

    for(var name in EVENT) {
        var code = EVENT[name];
        code_map[code] = name;
    }

    EVENT.find_event_name = function (code) {
        return code_map[code];
    };
})();

})(window);
