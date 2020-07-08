from django.db import models


class Group(models.Model):
    number = models.IntegerField(unique=True, primary_key=True)
    name = models.CharField(unique=True, max_length=15)


class Period(models.Model):
    number = models.IntegerField()


class Orbital(models.Model):
    name = models.CharField(max_length=20)


class Block(models.Model):
    name = models.CharField(max_length=1)


class IonisationEnergies(models.Model):
    ENERGY_UNIT = "kJ⋅mol⁻¹"  # constant
    DATA_SOURCE = "https://en.wikipedia.org/wiki/Ionization_energies_of_the_elements_(data_page)"

    atomic_number = models.IntegerField()
    ionisation_number = models.IntegerField()
    energy = models.DecimalField(max_digits=20, decimal_places=6)


class OxidationState(models.Model):
    state = models.CharField(max_length=3)


class Element(models.Model):
    atomic_number = models.IntegerField(unique=True, primary_key=True)
    name = models.CharField(unique=True, max_length=40)
    symbol = models.CharField(unique=True, max_length=2)
    group = models.ForeignKey(Group, on_delete=models.DO_NOTHING)
    period = models.ForeignKey(Period, on_delete=models.DO_NOTHING)

    # physical properties
    melting_point_kelvin = models.DecimalField(max_digits=20, decimal_places=6)
    boiling_point_kelvin = models.DecimalField(max_digits=20, decimal_places=6)
    atomic_mass_u = models.DecimalField(max_digits=20, decimal_places=6)
    atomic_radius = models.DecimalField(max_digits=20, decimal_places=6)

    # chemical properties
    oxidation_states = models.ManyToManyField(OxidationState)
    electronegativity = models.DecimalField(max_digits=20, decimal_places=6)
    electron_affinity = models.DecimalField(max_digits=20, decimal_places=6)
    electron_configuration = models.DecimalField(max_digits=20, decimal_places=6)

    # other
    year_discovered = models.IntegerField()
    discovered_by = models.CharField(max_length=100)
    estimated_crustal_abundance = models.CharField(max_length=20)  # !FIXME
    estimated_oceanic_abundance = models.CharField(max_length=20)  # !FIXME
    estimated_universal_abundance = models.CharField(max_length=20)  # !FIXME


class Isotope(models.Model):
    pass