import re
import logging

from Model.Star import Star
from Parser import Parser
from Model.Catalogue import Catalogue
from Model.Composition import Composition


class HypatiaParser(Parser):
    def __init__(self, filepath):
        super(HypatiaParser, self).__init__(filepath)

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
            raw_stars = f.read().strip().split("\n\n")  # Assumption: Each star is separated by ONE blank line
            logging.info("%s stars found in the file\n", len(raw_stars))
            for i, raw_star in enumerate(raw_stars):
                try:
                    logging.info("Started parsing star (%s)", i)
                    s = Star(None)
                    elements = []  # a list of catalogue and composition instances for the star
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
                            comp_cat = re.match(r'(\w+)(.*)\[(.+)\]', raw_attr)
                            if comp_cat:
                                element, value, author_year = comp_cat.groups()
                                catalogue = Catalogue(author_year)
                                composition = Composition(None, None, element, value)
                                elements.append([catalogue, composition])
                            else:
                                logging.warning('Unknown composition of star, "%s". Line unable to parse: "%s"',
                                                s.columns['hip'], raw_attr)
                    yield [s, elements]
                except:
                    # Pass the exception to be handled at the higher level
                    raise
