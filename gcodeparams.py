class GcodeParams:
    """
    Stores various coordinate offsets.

    Example:
    [G54:4.000,0.000,0.000]
    [G55:4.000,6.000,7.000]
    [G56:0.000,0.000,0.000]
    [G57:0.000,0.000,0.000]
    [G58:0.000,0.000,0.000]
    [G59:0.000,0.000,0.000]
    [G28:1.000,2.000,0.000]
    [G30:4.000,6.000,0.000]
    [G92:0.000,0.000,0.000]
    [TLO:0.000]
    [PRB:0.000,0.000,0.000:0]

    https://github.com/gnea/grbl/wiki/Grbl-v1.1-Commands#grbl--commands
    """
    def __init__(self, raw_data: str):
        self._raw_data = raw_data
        self._state = dict()

        self._parse_raw_data()

    def __str__(self):
        return f'<CalibrationState($#) {self._state}>'

    def _parse_raw_data(self):
        lines = self._raw_data.strip().split('\n')[:-1]
        for line in lines:
            line = line.strip()[1:-1]
            if line.startswith('TLO'):
                self._state['TLO'] = self._parse_tlo(line)
            elif line.startswith('PRB'):
                self._state['PRB'] = self._parse_prb(line)
            else:
                self._state[line[:3]] = self._parse_g(line)

    @staticmethod
    def _parse_tlo(raw: str):
        """
        Parses Tool Length Offset state string.

        [TLO:0.000] -> {'val': value}
        """
        _, value = raw.split(':')
        return {'val': value}

    @staticmethod
    def _parse_prb(raw: str):
        """
        Parses Probe cycle results.

        [PRB:0.000,0.000,0.000:0] -> {'x': x, 'y': y, 'z': z, 'ok': ok}
        """
        _, coords, ok = raw.split(':')
        x, y, z = map(float, coords.split(','))
        return {'x': x, 'y': y, 'z': z, 'ok': bool(ok)}

    @staticmethod
    def _parse_g(part: str):
        _, *coords = part.strip().lstrip('[').rstrip(']').split(':')
        x, y, z = map(float, coords[0].split(','))
        return {'x': x, 'y': y, 'z': z}

    @property
    def g54(self):
        return self._state['G54']

    @property
    def prb(self):
        return self._state['PRB']

    @property
    def tlo(self):
        return self._state['TLO']
