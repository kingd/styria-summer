import logging

from django.core.management.base import BaseCommand

from feeddler.models import Feeder


class Command(BaseCommand):
    args = ''
    help = 'Fetches active feeds and saves its entries to the database'

    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO)
        feeder = Feeder()
        feeder.process_feeds()
