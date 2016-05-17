import re

from Config import logger
from Model.Star import Star
from Parser import Parser
from Model.Catalogue import Catalogue
from Model.Composition import Composition
from Model.Planet import Planet


class HypatiaExoParser(Parser):
    def __init__(self, filepath):
        super(HypatiaExoParser, self).__init__(filepath)

    # Note: Keys should be in lower case
    column_map = {
        'hip': 'hip',
        'hd': 'hd',
        'bd': 'bd',
        'hr': 'hr',
        'spec type': 'spec',
        'vmag': 'vmag',
        'b-v': 'bv',
        'dist (pc)': 'dist',
        'ra/dec': ['rascension', 'declination'],
        'ra': 'rascension',
        'dec': 'declination',
        'position': 'position',
        'disk component': 'disk',
        'uvw': 'uvw',
        'teff': 'teff',  # exo planets columns from here
        'logg': 'logg',
        'mass(m_s)': 'mass',
        'vsini (km/s)': 'vsini',
        'multiple planets': 'multiple_planets'
    }

    def next(self):
        """
        Fetches the next star from Custom Hypatia format
        :return: Star instance
        """
        with open(self.path) as f:
            raw_stars = f.read().strip().split("\n\n")  # Assumption 251020: Each star is separated by ONE blank line
            logger.info("%s stars found in the file\n", len(raw_stars))
            for i, raw_star in enumerate(raw_stars):
                try:
                    logger.info("Started parsing star (%s)", i)
                    s = Star(None)
                    elements = []  # a list of catalogue and composition instances for the star
                    planets = []
                    raw_star_attrs = raw_star.split("\n")  # Assumption 251021: Each attribute of star is on a new line
                    for raw_attr in raw_star_attrs:
                        # Split attributes and values of the star. They are separated by a '=' or ':'
                        # Once split, the last entity is value and the last but one is the key
                        attr_value = re.split(r'=|:', raw_attr)
                        if len(attr_value) > 1:
                            key = attr_value[-2].lower().strip()

                            # Handle Multiple Planets Key
                            if attr_value[0].find('Multiple planets') >= 0:
                                key = 'multiple planets'
                            # Extract planet information
                            if re.match(r'\[[a-z]\]', attr_value[0]):  # if a line starts with [a-z]
                                p = self._parse_planet(raw_attr, s.columns.get('hip', 'UNK'))
                                if p:
                                    planets.append(p)

                            value = attr_value[-1].strip()
                            if key in self.column_map:
                                # Handling NULL values
                                if value == '999.0' and key != 'uvw':
                                    value = None
                                elif value.find('9999.0') >= 0 and key == 'uvw':
                                    value = None
                                s.set(self.column_map[key], value)
                        else:
                            comp_cat = re.match(r'(\w+)(.*)\[(.+)\]', raw_attr)
                            if comp_cat:
                                element, value, author_year = comp_cat.groups()
                                catalogue = Catalogue(author_year)
                                composition = Composition(None, None, element, value)
                                elements.append((catalogue, composition))
                            else:
                                logger.warning('Unknown composition of star, "%s". Line unable to parse: "%s"',
                                               s.columns.get('hip', 'UNK'), raw_attr)
                    yield s, elements, planets
                except:
                    # Pass the exception to be handled at the higher level
                    raise

    @staticmethod
    def _parse_planet(line, hip):
        """
        Parses a given line and returns a Planet instance
        Example line: [f] M_p = 0.0743252 +- 0.00521037(M_J), P = 122.72 +- 0.2(d), e = 0.133 +- 0.066, a = 0.49279 +- 0.0082306(AU)
        :param line: line to parse
        :return: Planet instance if no parsing error, else None
        """
        try:
            raw_name, raw_props = line.strip().split(' ', 1)
            name = re.match(r'\[([a-z])\]', raw_name).group(1)
            values = []
            for prop in raw_props.split(','):
                _, val = [p.strip() for p in prop.split('=')]
                values.append(re.match(r'[0-9 .+-]+', val).group())  # extract 0.07 +- 0.005 from 0.07 +- 0.005(M_J)
            mp, p, e, a = values  # Assumption 251026: M_p, P, e, a planet information should be in the same order
            return Planet(name, None, mp, p, e, a)
        except:
            logger.warning('Unknown planet information of star, %s. Unable to parse: %s', hip, line)
