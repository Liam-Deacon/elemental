"""A convenience wrapper for creating periodic table data with Django SQL ORM models.""" 
import sys
import re
import os
import json
import numpy as np

from pprint import pprint
from tqdm import tqdm 

from django.core.management.base import BaseCommand
from api.models import (
    Block, Element, Group, IonisationEnergies, Isotope,
    Orbital, OxidationState, Period
)

def remove_brackets(x):
    return re.sub(r'[\(\[][A-Za-z0-9 \.]{1,}[\)\]]', '', str(x))

def remove_colon_phrase(x):
    return re.sub(r'[A-Za-z]+:[ ]{0,}', '', str(x))

def numeric_cast(x):
    if isinstance(x, str):
        try:
            x = np.mean(eval(str(x)))
        except SyntaxError:
            x = eval(str(x))
    return x


def split_unit(x, value_cast=numeric_cast):
    try:
        value, unit, *_ = \
            tuple(map(str.strip,
                      re.sub(r'(â.*|\\x[0-9a-fA-f]{2}|~)', '',
                             remove_colon_phrase(remove_brackets(x))).split()))
    except ValueError as err:
        try:
            value, unit, *_ = x.partition('°C')
            value = float(value)
            if unit == '°C':
                value, unit = (value - 272.16, 'K')
        except ValueError:
            print(f"Cannot split unit from {x!r} due to {err!r}", file=sys.stderr)
            return None, None
    try:
        retval = value_cast("".join([ch for ch in str(value) if ch.isnumeric()])), unit
    except SyntaxError:
        try:
            retval = float(value), unit
        except ValueError as err:
            print(f"Cannot convert {value!r} to float due to {err!r}", file=sys.stderr)
            retval = None, None
    except Exception as err:
        print(f"Failed to cast {value!r} due to {err!r}", file=sys.stderr)
        retval = value, unit
    return retval


class Command(BaseCommand):
    """Handle connection with Django manage.py."""
    args = '<foo bar ...>'  # TODO: fix this
    help = 'Populates database with periodic table data'  # TODO: 

    def _create_elements(self):
        elements = json.load(open('elements.json'))  # load from somewhere
        progress = tqdm(tuple(elements.items()))
        for num, element in progress:
            progress.set_description(f"Processing Element: {element['symbol']}...")
            d = {k: v for k, v in element.items()
                 if k not in ('isotopes', 'oxidation_states', 'about')
                 and not k.startswith('elemental_forms_')}
            _data = {}
            unitless_keys = ('van_der_waals_atomic_radius',
                         'empirical_atomic_radius', 'covalent_atomic_radius',
                         'melting_point', 'boiling_point', 'electron_affinity',
                         'first_ionisation_energy')
            for key in unitless_keys:
                if key not in d:
                    continue  # skip as no such key
                value, unit = split_unit(d.pop(key))
                if value is None or unit is None:
                    continue  # skip as data invalid
                unit = re.sub('[_]?[0-9]+', '', str(unit)) or ''
                if not unit:
                    continue  # unit data is corrupted
                unit = 'pm' if (unit.isnumeric() or not unit) else unit
                unit = {'k': 'kelvin'}.get(unit.lower(), unit.lower())
                key = f"{key}_{unit}".rstrip('_')
                if key not in unitless_keys and re.match('.*_$', key):
                    _data[key] = value

            for key in ('period', 'group'):
                _data[key] = int(re.sub('[\ \-A-Za-z]+', '',
                                 str(d.pop(key))) or "0") or -1

            _data['atomic_mass'] = np.mean(float(remove_brackets(d.pop('atomic_weight'))))
            _data['density_g_per_cm3'] = split_unit(d.pop('density', ''))[0]
            _data['uses'] = "\n".join(element.get('uses', '')) or None
            _data['description'] = element.get('description', element.get('about', '')) or None

            _data.update(**d)

            elem = Element(atomic_number=int(num), **_data)
            elem.save()

            for isotope, _data in element.get('isotopes', {}).items():
                progress.set_description(f"Processing Isotope: {isotope}...")
                _data['year_discovered'] = _data.pop('discovered', None) or None
                try:
                    atomic_mass = _data.pop('atomic_mass', "")
                    mass, unc = re.sub('[\(\[].*[\)\]]', '', str(atomic_mass).replace(' ', '')).split("±")
                    _data['atomic_mass'] = float(mass)
                    _data['atomic_mass_uncertainty'] = float(unc)
                except Exception as err:
                    print(f"Could not extract atomic mass from {atomic_mass!r} due to {err!r}",
                          file=sys.stderr)
                iso = Isotope(isotope, **_data)
                iso.save()
                # print(f"Saved isotope: {isotope}")

            # print(f"Saved element: {element['symbol']}")

    def handle(self, *args, **options):
        """Perform actions to manipulate database."""
        self._create_elements()
