# elemental

Elemental is a RESTful Django app for getting periodic table data

## Introduction

If you're a physicist or chemist chance are that you have needed to look up data about specific elements or
isotopes from the periodic table. Unfortunately, the data needed is often on multiple sites, and doesn't
lend itself to easily being copied.

Elemental aims to change this! By providing a REST API to getting chemical and physical data it allows
the opportunity to integrate with data pipelines or assists in creating your own front-end visualisations.

The API can be tested at [elemental.lightbytestechnology.co.uk/api/](https://elemental.lightbytestechnology.co.uk/api/) 

### REST API endpoints

- /elements
- /isotopes
- /blocks [planned]
- /groups [planned]
- /structures [planned]

## Examples

General API is as follows:

```bash
$ curl -X GET 'http://127.0.0.1:8000/api/elements/'
...
```

The API endpoints accept URL queries:

```bash
$ curl -X GET 'http://127.0.0.1:8000/api/elements/?symbol=H'  | python -m json.tool 
[
    {
        "allen_scale_electronegativity": 2.3,
        "appearance": null,
        "atomic_mass": 1.007975,
        "atomic_number": 1,
        "boiling_point_kelvin": null,
        "covalent_atomic_radius_pm": null,
        "density_g_per_cm3": 8.988e-05,
        "description": null,
        "discovered_by": null,
        "electron_affinity_ev": null,
        "electron_configuration": "1s1",
        "element_classification": "Non-metal",
        "empirical_atomic_radius_pm": null,
        "estimated_crustal_abundance": "1.40\u00d710^3 milligrams per kilogram",
        "estimated_oceanic_abundance": "1.08\u00d710^5 milligrams per liter",        "estimated_universal_abundance": null,
        "first_ionisation_energy_ev": null,
        "ground_level": "2S1/2",
        "group": 1,
        "melting_point_kelvin": null,
        "name": "Hydrogen",
        "pauling_scale_electronegativity": 2.2,
        "period": 1,
        ...
        "symbol": "H",
        ...
        "van_der_waals_atomic_radius_pm": null,
        "year_discovered": null
    }
]
```

Fields can be filtered as desired using URL queries:

```bash
$ curl -X GET 'http://127.0.0.1:8000/api/elements/?fields=symbol,name,atomic_number&symbol=H,He' | python -m json.tool
[
    {
        "atomic_number": 1,
        "name": "Hydrogen",
        "symbol": "H"
    }
]
```

Or for idividual Elements or Isotopes:

```bash
curl -X GET 'http://127.0.0.1:8000/api/elements/2/?fields=symbol,atomic_mass' 2>/dev/null | python -m json.tool
{
    "atomic_mass": 4.002602,
    "symbol": "He"
}
```

```bash
curl -X GET 'http://127.0.0.1:8000/api/elements/2/' 2>/dev/null | python -m json.tool
{
    "abundance": 0.9975700000000001,
    "atomic_mass": 15.9949146196,
    "atomic_mass_uncertainty": 1.7e-10,
    "decay_modes": "IS=99.757\u00b11.6%",
    "element": "O",
    "halflife": "Stable",
    "isotope": "16O",
    "neutrons": 16,
    "year_discovered": 1919
}
```

NOTE: The trailing backslashes are important (because the REST API is implemented using Django, 
which believes URLs should be beautiful).

Enjoy!

Dr [Liam Deacon](mailto://liam.deacon@lightbytestechnology.co.uk)
