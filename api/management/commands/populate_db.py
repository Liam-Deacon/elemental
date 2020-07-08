"""A convenience wrapper for creating periodic table data with Django SQL ORM models.""" 
from django.core.management.base import BaseCommand
from api.models import (
    Block, Element, Group, IonisationEnergies, Isotope,
    Orbital, OxidationState, Period
)


class Command(BaseCommand):
    """Handle connection with Django manage.py."""
    args = '<foo bar ...>'  # TODO: fix this
    help = 'Populates database with periodic table data'  # TODO: 

    def _create_elements(self):
        elements = []  # load from somewhere
        for element in elements:
            element_orm = Element()
            element_orm.save()

    def handle(self, *args, **options):
        """Perform actions to manipulate database."""
        self._create_elements()
