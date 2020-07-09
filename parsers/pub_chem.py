"""This module scrapes PubChem database and collects the data as json."""
import sys
import re
import requests
import json
import numpy as np
from pprint import pprint


class PubChemDataParser:
    URL_BASE: str = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/element/{0}/JSON/?response_type=display"
    DATA_CACHE = {}


    def __init__(self, atomic_number: int):
        self.atomic_number = int(atomic_number)
        if self.atomic_number not in self.__class__.DATA_CACHE:
            req = requests.get(self.URL_BASE.format(self.atomic_number))
            self.__class__.DATA_CACHE[self.atomic_number] = json.loads(req.text.replace('Â', ''))

    @property
    def data(self):
        return self.DATA_CACHE[self.atomic_number]

    def parse_data(self, record=None):
        data = {}

        # use closure
        def get_section_string(info_idx=0, markup_idx=0, evaluate=False):
            try:
                value = section['Information'][info_idx]['Value']
                if markup_idx is None:
                    data = [k['String'] for k in value['StringWithMarkup']]
                else:
                    data = value['StringWithMarkup'][markup_idx]['String']
            except Exception as err:
                data = f"{np.mean(eval(str(value['Number'])))} {value['Unit']}"
            if evaluate:
                try:
                    data = eval(str(data))  # convert if possible
                except:
                    pass
            return data if not isinstance(data, str) else data.strip()

        def cast(x):
            try:
                return np.mean(eval(re.sub('\([0-9A-Za-z]{1,}\)',
                                           '', str(x).replace(' ', ''))))
            except:
                print(f"Unable to cast {x!r}", file=sys.stderr)
                return None if str(x).replace(' ', '') == '' else x

        section_mapping = {
            "Element Symbol": "symbol",
            "Element Name": "name",
            "Ground Level": "ground_level",
            "Ionization Energy": "first_ionisation_energy",
            "Electron Affinity": "electron_affinity",
            "Element Classification": "element_classification",
            "Element Period Number": "period",
            "Element Group Number": "group",
            "Density": "density",
            "Melting Point": "melting_point",
            "Boiling Point": "boiling_point",
            "Estimated Crustal Abundance": "estimated_crustal_abundance",
            "Estimated Oceanic Abundance": "estimated_oceanic_abundance",
            "Description": "description"
        }

        record = record or self.data['Record']
        for section in record['Section']:
            heading = section['TOCHeading']
            if 'Section' in section:
                data.update(self.parse_data(section))
            elif heading in section_mapping:
                data[section_mapping[heading]] = get_section_string()
            elif heading == "Element Name":
                data['name'] = get_section_string()
            elif heading == "History":
                continue
                _d =  "\n\n".join(['\n'.join([ss['Value']['StringWithMarkup'][0]['String'] for ss in s])
                                   for s in section['Information']])
                pprint(section['Information'])
            elif heading == "Electron Configuration":
                data['electron_configuration'] = get_section_string()
            elif heading in ("Atomic Radius", "Electronegativity"):
                _data = section['Information']
                d = {_data[i]['Name'].lower()
                                     .replace(' ', '_'):
                        re.sub(' \([A-Za-z\ ]+\)', '', get_section_string(i))
                     for i in range(len(_data))}
                data.update(d)
            elif heading == "Atomic Weight":
                data['atomic_weight'] = cast(get_section_string())
            elif heading == "Oxidation States":
                data['oxidation_states'] = \
                    sorted(get_section_string().replace(', ', ',').split(','))
            elif heading in ('InChI', 'InChI Key', 'Atomic Spectra',
                             'Physical Description'):
                pass  # skip
            elif heading in ("Uses", "Sources"):
                #continue  # delete when desired
                n = len(section['Information'])
                data[heading.lower()] = [
                    "\n".join(get_section_string(i, None)) for i in range(n)
                ]
            elif heading in ("Element Forms"):
                _data = section['Information']
                d = {'elemental_forms_'+_data[i]['Name'].lower()\
                                                        .replace(' ', '_'):
                     get_section_string(i) for i in range(len(_data))}
                data.update(d)
            elif heading == "Isotope Mass and Abundance":
                def clean_key(x):
                    x = re.sub(' \(.*', '', x).lower().strip().replace(' ', '_')
                    return x+'s' if x == "isotope" else "isotopic_" + x

                d = {clean_key(section['Information'][i]['Name']):
                     get_section_string(i, None) for i in range(len(section['Information']))}
                isotopes = data.get('isotopes', {})

                for i in range(len(d['isotopes'])):
                    isotope = d['isotopes'][i].strip()
                    isotopes[isotope] = isotopes.get(isotope, {}) 
                    isotopes[isotope].update({
                        'abundance': cast(d['isotopic_abundance'][i]),
                        'atomic_mass': cast(d['isotopic_atomic_mass'][i])
                    })

                data['isotopes'] = isotopes
            elif heading in ('Atomic Mass, Half Life, and Decay'):
                #pprint(section['Information'])
                mapping = {
                    "Atomic Mass and Uncertainty [u]": "atomic_mass",
                    "Decay Modes, Intensities and Uncertainties [%]": "decay_modes",
                    "Discovery Year": "discovered",
                    "Half Life and Uncertainty": "halflife",
                    "Nuclide": "isotope"
                }
                d = {
                    mapping[section['Information'][i]['Name']]: 
                        get_section_string(i, None)
                            for i in range(len(section['Information']))
                }
                data['isotopes'] = data.get('isotopes', {})
                for i, isotope in enumerate(d['isotope']):
                    _d = data['isotopes'].get(isotope, {})
                    _d.update({key: d[key][i] for key in mapping.values()
                               if key != "isotope"})
                    data['isotopes'][isotope] = _d
                continue  # skip for now
            else:
                pprint((heading, section['Information']))
                #data[section['TOCHeading']] = tuple(data.keys())
                break  # testing

        # apply formatting fixes
        for key in ('estimated_crustal_abundance',
                    'estimated_oceanic_abundance'):
            if key in data:
                data[key] = data[key].replace('Ã\x9710', '×10^')

        for key in data:
            if isinstance(data[key], str):
                data[key] = data[key].replace('Â', ' ')

        return data


if __name__ == "__main__":
    # collect data and output elements.json
    elements = {}
    for i in range(1, 119):
        try:
            elements[i] = PubChemDataParser(i).parse_data()
            print(f"Parsed element {i}")
        except Exception as err:
            print(f"Could not parse element {i} due to {err!r}",
                  file=sys.stderr)
    with open('elements.json', 'w') as f:
        json.dump(elements, f)
