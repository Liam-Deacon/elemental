from django.db import models
from computedfields.models import computed, ComputedFieldsModel
from json_field import JSONField


class Group(models.Model):
    number = models.IntegerField(unique=True, primary_key=True, default=1)
    name = models.CharField(unique=True, max_length=15, null=True)
    description = models.CharField(max_length=10000)


class Period(models.Model):
    number = models.IntegerField(unique=True, primary_key=True, default=1)
    name = models.CharField(unique=True, max_length=15, null=True)
    description = models.CharField(max_length=10000)


class Orbital(models.Model):
    name = models.CharField(max_length=20)
    ms_quantum_number = models.IntegerField(default=0.5)
    l_quantum_number = models.IntegerField(default=0)
    n_quantum_number = models.IntegerField(default=1)
    # image = models.ImageField()


class Block(models.Model):
    name = models.CharField(max_length=1)
    description = models.CharField(max_length=10000)
    groups = JSONField()


class CrystalStructure(models.Model):
    symmetry = models.CharField(max_length=20)
    a = models.FloatField()
    b = models.FloatField()
    c = models.FloatField()
    α = models.FloatField()
    β = models.FloatField()
    γ = models.FloatField()
    name = models.CharField(max_length=20)


class IonisationEnergies(models.Model):
    ENERGY_UNIT = "kJ⋅mol⁻¹"  # constant
    DATA_SOURCE = "https://en.wikipedia.org/wiki/Ionization_energies_of_the_elements_(data_page)"

    atomic_number = models.IntegerField()
    ionisation_number = models.IntegerField()
    energy = models.FloatField()


class Element(models.Model):
    atomic_number = models.IntegerField(unique=True, primary_key=True)
    name = models.CharField(unique=True, max_length=40, null=False)
    symbol = models.CharField(unique=True, max_length=2, null=False)
    group = models.IntegerField(null=False)
    period = models.IntegerField(null=False)

    # physical properties
    melting_point_kelvin = models.FloatField(null=True)
    boiling_point_kelvin = models.FloatField(null=True)
    atomic_mass = models.FloatField(null=True)
    empirical_atomic_radius_pm = models.FloatField(null=True)
    covalent_atomic_radius_pm = models.FloatField(null=True)
    van_der_waals_atomic_radius_pm = models.FloatField(null=True)
    density_g_per_cm3 = models.FloatField(null=True)

    # chemical properties
    pauling_scale_electronegativity = models.FloatField(null=True)
    allen_scale_electronegativity = models.FloatField(null=True)
    electron_affinity_ev = models.FloatField(null=True)
    electron_configuration = models.CharField(max_length=50, null=True)
    ground_level = models.CharField(max_length=50, null=True)
    first_ionisation_energy_ev = models.FloatField(null=True)

    # other
    # image = models.ImageField()
    element_classification = models.CharField(max_length=30, null=True)
    appearance = models.CharField(max_length=100, null=True)
    year_discovered = models.IntegerField(null=True)
    discovered_by = models.CharField(max_length=100, null=True)
    estimated_crustal_abundance = models.CharField(max_length=20, null=True)  # !FIXME
    estimated_oceanic_abundance = models.CharField(max_length=20, null=True)  # !FIXME
    estimated_universal_abundance = models.CharField(max_length=20, null=True)  # !FIXME
    description = models.CharField(max_length=5000, null=True)
    sources = models.CharField(max_length=3000, null=True)
    uses = models.CharField(max_length=3000, null=True)


class OxidationState(models.Model):
    symbol = models.CharField(max_length=2, null=False, default="H")
    state = models.IntegerField(primary_key=True, null=False)


class Isotope(models.Model):
    isotope = models.CharField(primary_key=True, max_length=10, default="1H")
    abundance = models.FloatField(null=True)
    atomic_mass = models.FloatField(null=True)
    atomic_mass_uncertainty = models.FloatField(null=True)
    decay_modes = models.CharField(max_length=80, null=True)
    year_discovered = models.IntegerField(null=True)
    halflife = models.CharField(max_length=30, null=True)

    # @computed(models.CharField(max_length=2, null=False),
    #           depends=[['self', ['isotope']]])
    # def element(self):
    #     return "".join([ch for ch in self.isotope if ch.isalpha()])

    @property
    def element(self):
        return "".join([ch for ch in self.isotope if ch.isalpha()])

    @property
    def neutrons(self):
        """Get number of neutrons for isotope."""
        return int("".join([ch for ch in self.isotope if ch.isnumeric()]))
