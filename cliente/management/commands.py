from django.core.management.base import BaseCommand
from .commands.load_data import load_data_from_csv

class Command(BaseCommand):
    help = 'Load data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='CSV file path')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        load_data_from_csv(csv_file)
