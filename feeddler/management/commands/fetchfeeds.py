import re
from datetime import datetime

import feedparser
from bs4 import BeautifulSoup
from django.db import transaction
from django.core.management.base import BaseCommand

from feeddler.models import Feed, Word, Entry, FeedWord, EntryWord


class Command(BaseCommand):
    args = ''
    help = 'Fetches active feeds and saves its entries to the database'

    def handle(self, *args, **options):
        feeds = Feed.objects.filter(is_active=True)
        for feed in feeds:
            print(type(feed.last_modified))
            print(feed.last_modified)
            print(feed.etag)
            print()
            rss = feedparser.parse(feed.link, modified=feed.last_modified,
                                   etag=feed.etag)

            if rss.feed:
                feed.title = rss.feed.title
                self.stdout.write("Feed: %s" % feed)
                if 'etag' in rss:
                    print('etag', rss.etag)
                    feed.etag = rss.etag
                if 'modified' in rss:
                    print('modified', rss.modified)
                    print('modified_parsed', rss.modified_parsed)
                    modified = self.time_to_datetime(rss.modified_parsed)
                    feed.last_modified = modified
                feed.save()

                if 'status' in rss:
                    print('status', rss.status)
                for entry in rss.entries:
                    words = []
                    content = ''
                    title = ''
                    if 'link' in entry:
                        link = entry.link
                    if 'title' in entry:
                        title = entry.title
                    if 'content' in entry:
                        for c in entry.content:
                            if 'value' in c:
                                value = c.value
                                words.extend(self.extract_words(value))
                        content += value
                    elif 'summary' in entry:
                        value = entry.summary
                        words = self.extract_words(value)
                        content = value
                    db_entry = Entry.objects.filter(
                        feed=feed, link=link).first()
                    if db_entry is not None:
                        db_entry.title = title
                        db_entry.content = value
                        db_entry.save()
                    else:
                        db_entry = Entry(feed=feed, link=link, title=title,
                                         content=value)
                        db_entry.save()
                        self.save_words(words, db_entry, feed)
            else:
                self.stdout.write("Not modified, skipping: %s" % feed)

    def time_to_datetime(self, time_struct):
        # import pytz
        # utc = pytz.utc
        # return utc.localize(datetime(*time_struct[:6])).isoformat()
        from django.utils import timezone
        date = datetime(*time_struct[:6])
        date = timezone.make_aware(date, timezone.get_current_timezone())
        return date.isoformat()

    def extract_words(self, content):
        soup = BeautifulSoup(content)
        content = soup.get_text().lower()
        regex = re.compile(ur'\w+', re.UNICODE)
        words = regex.findall(content)
        return words

    @transaction.atomic
    def save_words(self, words, entry, feed):
        self.stdout.write('Saving: %s words' % len(words))
        for w in words:
            word, is_created = Word.objects.get_or_create(word=w)
            word.count += 1
            word.save()

            feed_word = FeedWord.objects.filter(feed=feed, word=word).first()
            if feed_word is None:
                feed_word = FeedWord(feed=feed, word=word)
            feed_word.count += 1
            feed_word.save()

            entry_word = EntryWord.objects.filter(
                entry=entry, word=word).first()
            if entry_word is None:
                entry_word = EntryWord(entry=entry, word=word)
            entry_word.count += 1
            entry_word.save()
