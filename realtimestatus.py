from enum import Enum, auto


class State(Enum):
    Idle = 0
    Run = auto()
    Hold = auto()
    Jog = auto()
    Alarm = auto()
    Door = auto()
    Check = auto()
    Home = auto()
    Sleep = auto()


class RealtimeStatus:
    """
    Stores Grbl Real-time status

    <Idle|MPos:0.000,0.000,0.000|FS:0,0|WCO:0.000,0.000,0.000>
    <Idle|MPos:0.000,0.000,0.000|FS:0,0|Ov:100,100,100>
    <Idle|MPos:0.000,0.000,0.000|FS:0,0>

    https://github.com/gnea/grbl/wiki/Grbl-v1.1-Interface#grbl-response-messages
    """

    def __init__(self, raw: str):
        self._raw = raw
        self._state = dict()

        self._parse_raw_data()

    def __str__(self):
        return f'<RealtimeState(?) {self._state}>'

    def _parse_raw_data(self):
        temp = self._raw.strip().split('\n')[0].strip()
        state, *rest = temp[1:-1].split('|')
        self._parse_state(state)
        for line in rest:
            self._parse_line(line)

    def _parse_state(self, state_str):
        state, *substate = state_str.split(':')
        self._state.update({'state': State[state], 'substate': substate[0] if substate else None})

    def _parse_line(self, line: str):
        if line.startswith('FS'):
            self._state.update({k: v for k, v in zip(('feed', 'speed'), map(float, line.split(':')[1].split(',')))})
        elif line.startswith('MPos'):
            self._state.update({'mpos': {k: v for k, v in zip(('x', 'y', 'z'), map(float, line.split(':')[1].split(',')))}})
        elif line.startswith('WPos'):
            self._state.update({'wpos': {k: v for k, v in zip(('x', 'y', 'z'), map(float, line.split(':')[1].split(',')))}})
        elif line.startswith('WCO'):
            self._state.update({'wco': {k: v for k, v in zip(('x', 'y', 'z'), map(float, line.split(':')[1].split(',')))}})
        elif line.startswith('Ov'):
            self._state.update({'ov': {k: v for k, v in zip(('x', 'y', 'z'), map(float, line.split(':')[1].split(',')))}})

    @property
    def probe(self):
        return self._state['mpos']

    @classmethod
    def default(cls):
        # TODO add normal constructor, move string parser to 'from_string' constructor
        return cls('<Idle|MPos:0.000,0.000,0.000|FS:0,0>')

    @property
    def state(self):
        return self._state['state']
