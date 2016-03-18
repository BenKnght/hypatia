import re

from Model.StarModel import Star
from Parser import Parser


class HypatiaParser(Parser):
    def __init__(self, filepath):
        Parser.__init__(self, filepath)

    # Note: Keys should be in lower case
    hypatia_column_map = {
        'hip': 'hip',
        'hd': 'hd',
        'bd': 'bd',
        'hr': 'hr',
        'spec type': 'spec',
        'vmag': 'vmag',
        'b-v': 'bv',
        'dist (pc)': 'dist',
        'ra/dec': ['rascension', 'declination'],
        'position': 'position',
        'disk component': 'disk',
        'uvw': 'uvw'
    }

    def next(self):
        """
        Fetches the next star from Custom Hypatia format
        :return: Star instance
        """
        with open(self.path) as f:
            raw_stars = f.read().split("\n\n")  # Assumption: Each star is separated by ONE blank line
            for raw_star in raw_stars:
                try:
                    s = Star(None)
                    raw_star_attrs = raw_star.split("\n")  # Assumption: Each attribute of the star is on its own line
                    for raw_attr in raw_star_attrs:
                        # Split attributes and values of the star. They are separated by a '=' or ':'
                        # Once split, the last entity is value and the last but one is the key
                        attr_value = re.split(r'=|:', raw_attr)
                        if len(attr_value) > 1:
                            key = attr_value[-2].lower().strip()
                            value = attr_value[-1].strip()
                            if key in self.hypatia_column_map:
                                if key == 'ra/dec':
                                    m = re.match(r'\((.+),(.+)\)', value)
                                    ra, dec = m.groups()
                                    s.set('rascension', float(ra.strip()))
                                    s.set('declination', float(dec.strip()))
                                else:
                                    s.set(self.hypatia_column_map[key], value)
                        else:
                            # composition attributes of star
                            pass
                    yield s
                except:
                    # TODO: Log that a star has been skipped
                    raise
                    pass