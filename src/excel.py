import os
import string
import tempfile
import xlsxwriter

from model import Participant

# Look into config.js for more details!
APPLICATION_START = 1000
HEADER_ROW = 0
INFO_OFFSET = 5
SAVE_EVENT = 5
TMP = tempfile.gettempdir()


EVENT_NAMES = {
    1000: 'APPLICATION_START',
    1001: 'INSTRUCTIONS_START',
    1002: 'NEXT_PAGE',
    1003: 'INSTRUCTIONS_END',
    1004: 'EXPERIMENT_START',
    1005: 'CLOCK_START',
    1006: 'CLOCK_STOP',
    1007: 'TRIALS_LOADED',
    1008: 'PAUSE_START',
    1009: 'PAUSE_END',
    1010: 'EXPERIMENT_END',
    1020: 'CODE_START',
    1021: 'CODE_END',
    1: 'TRIAL_START',
    2: 'TRIAL_RUN',
    3: 'CHOOSE',
    4: 'CHECK',
    5: 'SAVE'
}


def split_header(header):
    return [fragment.strip() for fragment in header.split(',')]


_events_header = ('event name time').split(' ')
_trials_header = ('delta p1 p2 subrange_key sample_size '
                  'selection ticks timedelta empirical_delta empirical_p1 '
                  'empirical_p2 start_with left right timestamp ').split(' ')

_info_header = {
    'Object Id': (lambda p: str(p.get('_id'))),
    'Participant Id': (lambda p: p.get(Participant.KEY, 'NA')),
    'Tag': (lambda p: p.get('tag', 'NA')),
    'Created': (lambda p: str(p.get('_id').generation_time))
}


def _printable_name(name):
    alphabet = string.ascii_letters + string.digits
    return ''.join([(c if c in alphabet else '-') for c in name])


def _event_name(id_):
    return EVENT_NAMES.get(id_, 'ERROR')


def unpack(dict_, path, seperator='.'):
    path = path.split(seperator)
    for step in path:
        dict_ = dict_.get(step)
    return dict_


def sequence_to_string(sequence):
    return ''.join(map(str, sequence))

conversions = {
    'left': lambda e: sequence_to_string(unpack(e, 'steps')),
    'right': lambda e: sequence_to_string(unpack(e, 'steps'))
}


def ident(v):
    return v


class ParticipantWorkbook(object):

    def __init__(self, participant_document):
        self.participant = participant_document

    def write(self):
        options = {'constant_memory': True}
        excel_file_path = os.path.join(TMP, self._make_file_name())
        if os.path.isfile(excel_file_path):
            os.remove(excel_file_path)

        self.workbook = xlsxwriter.Workbook(excel_file_path, options)
        self._add_sheets()
        return excel_file_path

    def _add_sheets(self):
        self.worksheet = self.workbook.add_worksheet('System Events')

        self._add_participant_info()
        self._add_system_events()

        self.worksheet = self.workbook.add_worksheet('Trials')
        self._add_trials()

        self.workbook.close()

    def _make_file_name(self):
        PREFIX = 'participant'
        EXT = '.xlsx'
        tag = self.participant.get('tag') or ''
        tag = _printable_name(tag)
        id_ = self.participant.get(Participant.KEY) or ''
        return '-'.join([PREFIX, tag or id_]) + EXT

    def _add_participant_info(self):
        for i, (key, predicate) in enumerate(_info_header.items()):
            self.worksheet.write(i, 0, key + ':')
            self.worksheet.write(i, 1, predicate(self.participant))

    def _add_system_events(self):
        # Filter Events
        trials = self.participant.get('trials')
        events = (event
                  for event
                  in trials
                  if event.get('event') >= APPLICATION_START
                  )

        # Write Event Header
        for i, caption in enumerate(_events_header):
            self.worksheet.write(HEADER_ROW + INFO_OFFSET, i, caption)

        # Write Event Data
        for i, event in enumerate(events):
            row = HEADER_ROW + INFO_OFFSET + i
            event_id = event.get('event')
            self.worksheet.write(row, 0, event_id)
            self.worksheet.write(row, 1, _event_name(event_id))
            self.worksheet.write(row, 2, str(event.get('timestamp')))

    def _add_trials(self):
        # Filter Events
        trials = self.participant.get('trials')
        events = (event
                  for event in
                  trials
                  if event.get('data')
                  and event.get('event') == SAVE_EVENT
                  )

        # Write Event Header
        for i, caption in enumerate(_trials_header):
            self.worksheet.write(0, i, caption)

        for row, event in enumerate(events):
            for col, caption in enumerate(_trials_header):
                if caption == 'timestamp':
                    self.worksheet.write(row + 1, col, event.get('timestamp'))
                    continue
                data = event.get('data')
                conversion = conversions.get(caption, ident)
                value = conversion(data.get(caption))
                self.worksheet.write(row + 1, col, value)


class CompleteWorkbook(ParticipantWorkbook):

    HEADER = ("participant_id tag timestamp "
              "delta p1 p2 subrange_key "
              "empirical_delta empirical_p1 empirical_p2 "
              "sample_size ticks timedelta selection "
              "start_with last_left last_right left right").split(' ')

    RENAME = {
        "timedelta": "duration_ms",
        "start_with": "started_right",
        "selection": "selected_right"
    }

    CONVERSIONS = {
        'left': sequence_to_string,
        'right': sequence_to_string,
    }

    def __init__(self, events):
        self.events = events

    def _make_file_name(self):
        return "participants-all.xlsx"

    def _add_sheets(self):
        self.worksheet = self.workbook.add_worksheet('Events')

        # Write header
        for j, caption in enumerate(self.HEADER):
            caption = self.RENAME.get(caption, caption)
            self.worksheet.write(0, j, caption)

        # Write data
        for i, event in enumerate(self.events):
            for j, caption in enumerate(self.HEADER):
                data = event.get(caption)
                data = self.CONVERSIONS.get(caption, ident)(data)
                self.worksheet.write(i + 1, j, data)
