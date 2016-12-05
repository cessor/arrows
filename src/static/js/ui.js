(function(window) {

function Grid(element) {
    function Arrow(direction) {
        // direction is either UP or DOWN
        var self = this;
        var image = $('<img>')
            .attr('src', arrows[direction])
            .css('position', 'fixed');

        this.attachAt = function (point, element) {
            image
            .css({
                 'left': element.offset().left + point[0] + "px"
                , 'top': element.offset().top + point[1] + "px"
                , 'width': point[2] + "px"
                , 'height': point[3] + "px"
            })
            .appendTo(element);
        };
    }

    // A grid manages a field with A x B cells.
    // When updating, we select a random cell to  an arrow in.
    // This for each cell, we calculate the pixel location to
    // the arrow at.

    var positions = {};

    function mapToCellPixel (position) {

        var cell_width =  Math.floor(element.outerWidth() / GRID_COLUMNS);
        var cell_height = Math.floor(element.outerHeight() / GRID_ROWS);

        var col = position[0];
        var row = position[1];

        var width = cell_width - ARROW_PADDING;
        var height = cell_height - ARROW_PADDING;

        // Get to the center of cell
        var center_x = (col * cell_width) + (cell_width / 2);
        var center_y = (row * cell_height) + (cell_height / 2);

        // Calculate offset for image hook (topleft corner)
        var pivot_x = Math.round((center_x - (width / 2)));
        var pivot_y = Math.round((center_y - (height / 2)));

        return [
            pivot_x,
            pivot_y,
            width,
            height
        ];
    }

    function generateUniquePosition () {

        function spaceLeft () {
            var a = Object.keys(positions).length;
            var b = (GRID_COLUMNS * GRID_ROWS);
            return  a < b;
        }

        function randomPosition () {
            return [
                Math.floor(Math.random() * GRID_COLUMNS),
                Math.floor(Math.random() * GRID_ROWS)
            ];
        }

        if(!spaceLeft()) {
            return null;
        }

        var position = randomPosition();
        while(positions[position] && spaceLeft()) {
            position = randomPosition();
        }

        positions[position] = true;
        return position;
    }

    this.hide = function () {
        element.hide();
    }

    this.show = function () {
        element.show();
    }

    this.clear = function () {
        positions = {};
        element.empty();
    };

    this.update = function (direction) {
        var position = generateUniquePosition();

        if(position == null) {
            return;
        }

        var location = mapToCellPixel(position);
        new Arrow(direction)
            .attachAt(location, element)

        return [direction, position];
    };
}


function Hourglass(element, options) {
    var self = this;

    options = options || {};

    var color = options.color || '#1155cc';
    var white = '#ffffff';

    var canvas = document.createElement('canvas');
    var context = canvas.getContext('2d');
    context.imageSmoothingEnabled = false;

    $(element).append(canvas);

    var width = 20;
    var height = 100;
    var padding = 4;

    function drawBox () {
        var w = width + padding;
        var center_x = ($(element).outerWidth() / 2) - (w / 2);
        context.beginPath();
        context.rect(center_x, 0, w, height);
        context.strokeStyle = color;
        context.stroke();
    }

    function drawPauseBox () {
        var w = width + (padding / 2);
        var height = 4;
        var center_x = ($(element).outerWidth() / 2) - (w / 2);
        var center_y = ($(element).outerHeight() / 2) - (height / 2);

        context.beginPath();
        context.rect(center_x, center_y, w, height);
        context.fillStyle = color;
        context.fill();
        context.strokeStyle = white;
        context.lineWidth = 2;
        context.stroke();
    }

    function fill(fillLevel, color) {
        // Too Small values produce ugly artifacts
        if(fillLevel < 5) {
            return;
        }
        fillLevel = Math.min(fillLevel, 100);
        var center_x = ($(element).outerWidth() / 2) - (width / 2);
        context.beginPath();
        var h = height - fillLevel + padding / 2; //
        context.rect(center_x, h, width, fillLevel - padding);
        context.fillStyle = color;
        context.fill();
    }

    this.fill = function (level) {
        fill(100, white);
        fill(level, color);
        drawPauseBox();
        drawBox();
    };

    this.reset = function () {
        fill(100, white);
        drawPauseBox();
        drawBox();
    };

    this.show = function () {
        $(element).show();
    };

    this.hide = function () {
        $(element).hide();
    };
}


function Keyboard(options) {
    function Keymap () {
        var self = this;Keyboard
        var code_to_name = {};
        var name_to_code = {
            // Controls
            "backspace": 8, "tab": 9, "return": 13, "shift": 16,
            "ctrl": 17, "alt": 18, "capslocks": 20,
            "esc": 27, "space": 32, "left": 37, "up": 38, "right": 39, "down": 40,
            "page-up": 33,  "page-down": 34, "end": 35, "home": 36,
            "insert": 45, "delete": 46,

            // Numbers
            "0": 48, "1": 49, "2": 50, "3": 51, "4": 52,
            "5": 53, "6": 54, "7": 55, "8": 56, "9": 57,

            // Alphabet
            "A": 65, "B": 66, "C": 67, "D": 68, "E": 69, "F": 70,
            "G": 71, "H": 72, "I": 73, "J": 74, "K": 75, "L": 76,
            "M": 77, "N": 78, "O": 79, "P": 80, "Q": 81, "R": 82,
            "S": 83, "T": 84, "U": 85, "V": 86, "W": 87, "X": 88,
            "Y": 89, "Z": 90,

            // FKeys
            "F1": 112,  "F2": 113,  "F3": 114,  "F4": 115,
            "F5": 116,  "F6": 117,  "F7": 118,  "F8": 119,
            "F9": 120, "F10": 121, "F11": 122, "F12": 123,

            // Special
            "windows-left": 91, "windows-right": 92
        };

        (function cacheCodes () {
            // Inverts the name:code pairs for faster lookup
            for (var name in name_to_code) {
                var code = name_to_code[name];
                code_to_name[code] = name;
            }
        })();

        self.code = function (name) {
            return name_to_code[name];
        };

        self.exists = function (name) {
            return (name in name_to_code);
        }
    }

    var self = this;
    var pause = false;
    var keymap = new Keymap();
    var on_down_map = {};
    var on_up_map = {};
    var on_press_map = {};
    var options = options || {
        'prevent_default': true
    };

    self.clear = function () {
        on_down_map = {};
        on_up_map = {};
        on_press_map = {};
        return self;
    };

    self.down = function (mappings) {
        register(mappings, on_down_map);
        return self;
    };

    self.released = function (mappings) {
        register(mappings, on_up_map);
        return self;
    };

    self.listen = function () {
        pause = false;
        document.removeEventListener('keydown', handleKeyDown);
        document.removeEventListener('keyup', handleKeyUp);
        document.addEventListener('keydown', handleKeyDown);
        document.addEventListener('keyup', handleKeyUp);
    }

    self.pause = function () {
        pause = true;
    }

    self.resume = function () {
        pause = false;
    }

    function register (mappings, target_map) {
        // Maps named keys and their functions to
        // Keycodes, like:
        // {space: func} --> {32: func}
        function mapActionToKey (key, action) {
            if(!keymap.exists(key)) {
                // Don't register bad keys
                return;
            }
            var code = keymap.code(key);
            target_map[code] = action;
        };

        for(var key in mappings) {
            var action = mappings[key];
            mapActionToKey(key, action);
        };
    }

    function handleKeyDown (event_) {
        handle(on_down_map, event_)
    }

    function handleKeyUp (event_) {
        handle(on_up_map, event_)
    }

    function handle (map, event_) {
        if(pause) {
            return;
        }
        var code = event_.keyCode;
        var action = map[code] || function () {};
        if (options.prevent_default) {
            event_.preventDefault();
        }
        action();
    }
}


function Arch (element, options) {
        // Defines the graphical Element for the progress indicator
        var options = options || {};

        var strokeWidth = options.strokeWidth || 20;
        var size = options.size || 100;
        var color = options.color || '#1155cc';
        var background = options.background || '#efefef';
        var lineCap = options.lineCap || 'butt';

        var canvas = document.createElement('canvas');
        var context = canvas.getContext('2d');
        context.imageSmoothingEnabled = true;
        $(element).append(canvas);

        canvas.width = size;
        canvas.height = size;

        // center
        context.translate(size / 2, size / 2);

        // start at the top
        context.rotate(-0.5 * Math.PI);

        var radius = (size - strokeWidth) / 2;

        function draw(color, strokeWidth, percent) {
            percent = Math.min(Math.max(0, percent || 1), 1);
            context.beginPath();
            context.arc(0, 0, radius, 0, Math.PI * 2 * percent, false);
            context.strokeStyle = color;
            context.lineCap = lineCap;
            context.lineWidth = strokeWidth;
            context.stroke();
        }

        this.reset = function () {
            context.clearRect(-size, -size, 2*size, 2*size);
            draw(background, strokeWidth, 1);
        }

        this.draw = function (percent) {
            draw(color, strokeWidth, percent / 100);
        };

        this.reset();
}


function Progress (element, max) {
    var self = this;
    self.max = max;
    self.value = 0;

    var label = $(document.createElement('span'));
    $(element).append(label);

    var arch = new Arch(element, {
        'background': '#aaa',
        'strokeWidth': 18
    });

    self.increase = function (value) {
        self.value = self.value + value || 1;
        arch.draw(self.value / self.max * 100);
    };

    self.reset = function (max) {
        self.value = 0;
        self.max = max;
        arch.reset();
    };

    self.label = function (text) {
        label.text(text);
    };

    self.hide = function () {
        element.hide();
    };

    self.show = function () {
        element.show();
    }
}


function ExperimentUI() {
    var self = this;

    this.trial = $('#trial');
    this.end = $('#end');

    // Controls
    var headline = $('#headline');
    var choice_a = $('#choice_a');
    var choice_b = $('#choice_b');
    var hint = $('#hint');
    var next = $('#next');
    var progress = new Progress($('#progress'), 0, 24);
    var clock = new Hourglass($('#hourglass'));
    var grid_left = new Grid($('#grid_left'));
    var grid_right = new Grid($('#grid_right'));
    var label_left = $('#label_left');
    var label_right = $('#label_right');
    var loading = $('#loading');
    var pause = $('#pause');
    var end = $('#end');

    this.startLoading = function () {
        loading.show();
    };

    this.stopLoading = function () {
        loading.hide();
    };

    this.pause = function () {
        pause.show();
    };

    this.end = function () {
        end.show();
    };

    this.choice = function () {
        choice_a.show();
        choice_b.show();
        grid_left.hide();
        grid_right.hide();
        hint.text(HINT_DECISION).show();
        label_left.hide();
        label_right.hide();
        next.hide();
        progress.hide();
        headline.show();
    };

    this.reset = function () {
        clock.show();
        choice_a.hide();
        choice_b.hide();
        grid_left.clear();
        grid_left.show();
        grid_right.clear();
        grid_right.show();
        headline.hide();
        hint.text(HINT_START).show()
        label_left.show();
        label_right.show();
        next.text(BUTTON_START).show();
        progress.label("");
        progress.reset(1);
        progress.show();
        pause.hide();
    };

    this.running = function (trial) {
        hint.hide();
        next.text(BUTTON_STOP).show();
        progress.label(trial.sample_size);
        progress.reset(trial.sample_size);
        progress.show();
    };

    this.setClock = function (progress_percent) {
        clock.fill(progress_percent);
    };

    this.resetClock = function () {
        clock.fill(1);
    };

    this.updateLeft = function (direction) {
        progress.increase(0.5);
        grid_left.update(direction);
    };

    this.updateRight = function (direction) {
        progress.increase(0.5);
        grid_right.update(direction);
    };

    new Image().src = ARROW_UP;
    new Image().src = ARROW_DOWN;
    clock.reset();
}


window.ExperimentUI = ExperimentUI;
window.Keyboard = Keyboard;
window.Arch = Arch;
window.Progress = Progress;

})(window);