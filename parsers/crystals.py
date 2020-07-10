"""A parser for the crystals python package to create JSON data."""
import crystals
import re
import json
import types
import numpy as np

from tqdm import tqdm


class CrystalSerialiser:
    """Class for serialising crystals.Crystal objects."""

    DEFAULT_EXCLUDES = ('builtins', 'reciprocal', 'reciprocal_vectors',
                        'valid_names', 'valid_symbols')

    @staticmethod
    def get_attributes(obj, specific_excludes=DEFAULT_EXCLUDES):
        """Retrieve desired attributes from obj, excluding problematic ones."""
        return {attr: getattr(obj, attr) for attr in dir(obj)
                if not attr.startswith('_')
                and not callable(getattr(obj, attr))
                and attr not in specific_excludes}

    @classmethod
    def serialise(cls, obj):
        """Serialise `obj` to JSON compatible types, calls recursively."""
        data = cls.get_attributes(obj)

        for key in ('lattice_system', 'centering'):
            if key in data:
                data[key] = \
                    ".".join(str(data[key]).split('.')[1:]) or data[key]

        if 'lattice_parameters' in data:
            data['lattice_parameters'] = \
                dict(zip(('a', 'b', 'c', 'α', 'β', 'γ'),
                         data['lattice_parameters']))

        if 'element_full' in data and 'element' in data:
            data.pop('element_full')
            data.pop('element')

        if 'lattice_vectors' in data:
            data['lattice_vectors'] = \
                [list(val) for val in data['lattice_vectors']]

        # convert arrays
        data.update({k: str(v) for k, v in data.items()
                     if isinstance(v, (crystals.ElectronicStructure,
                                       crystals.CenteringType))})
        data.update({k: cls.serialise(v) for k, v in data.items()
                     if isinstance(v, crystals.Lattice)})
        data.update({k: v.tolist() for k, v in data.items()
                     if isinstance(v, np.ndarray)})
        data.update({k: frozenset(v) for k, v in data.items()
                     if isinstance(v, types.GeneratorType)})

        data.update({k: [cls.serialise(vi) for vi in v]
                     for k, v in data.items() if isinstance(v, frozenset)})

        if 'source' in data:
            data['source'] = "/".join(re.split(r'[/\\]', data['source'])[-5:])

        if isinstance(obj, crystals.Crystal):
            data['symmetry'] = cls.serialise(obj.symmetry())

        return data


def serialise_crystals_data():
    """Serialise entire crystals package database."""
    crystal_data = {}
    with tqdm(tuple(crystals.Crystal.builtins)) as progress_bar:
        for name in progress_bar:
            progress_bar.set_description(f'Processing Crystal {name}...')
            crystal = crystals.Crystal.from_database(name)
            crystal_data[name] = CrystalSerialiser.serialise(crystal)
    return crystal_data


if __name__ == "__main__":
    crystal_data = serialise_crystals_data()
    with open('crystals.json', 'w') as f:
        json.dump(crystal_data, f)
