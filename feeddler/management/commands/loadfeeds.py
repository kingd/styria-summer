from django.core.management.base import BaseCommand

from feeddler.models import Feed


class Command(BaseCommand):
    args = ''
    help = 'Load test feeds into the database'
    feeds = (
        {'title': 'Ars Technica',
         'link': 'http://feeds.arstechnica.com/arstechnica/index/'},
        {'title': 'planet debian',
         'link': 'http://planet.debian.org/rss20.xml'},
        {'title': '24sata',
         'link': 'http://www.24sata.hr/feeds/najnovije.xml'},
    )

    def handle(self, *args, **options):
        for feed in self.feeds:
            db_feed, is_created = Feed.objects.get_or_create(
                title=feed['title'], link=feed['link'], is_active=True)
