import re
from datetime import datetime
from collections import OrderedDict
import logging

from django.db import models, transaction
from django.utils import timezone

from bs4 import BeautifulSoup
import feedparser


logger = logging.getLogger(__name__)


class Feed(models.Model):
    """Feeds."""
    link = models.URLField(max_length=512, unique=True)
    is_active = models.BooleanField('Active', default=False)
    title = models.CharField(max_length=1024, blank=True, null=True)
    last_modified = models.DateTimeField(blank=True, null=True)
    etag = models.CharField(max_length=512, blank=True, null=True)
    words = models.ManyToManyField("Word", through='FeedWord')
    entries = models.ManyToManyField("Entry")

    def __unicode__(self):
        return self.link


class Entry(models.Model):
    """Feed entries."""
    link = models.CharField(max_length=512, unique=True)
    title = models.CharField(max_length=512, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    words = models.ManyToManyField("Word", through='EntryWord')

    def __unicode__(self):
        if not self.title:
            return u'No title'
        return self.title


class Word(models.Model):
    """Words."""
    word = models.CharField(primary_key=True, max_length=64)
    count = models.IntegerField(default=0)

    def __unicode__(self):
        return u'%s - %s' % (self.word, self.count)


class FeedWord(models.Model):
    """Words in particular feed."""
    feed = models.ForeignKey(Feed)
    word = models.ForeignKey(Word)
    count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('feed', 'word')

    def __unicode__(self):
        return u'%s - %s - %s' % (self.feed.link, self.word.word, self.count)


class EntryWord(models.Model):
    """Words in particular feed entry."""
    entry = models.ForeignKey(Entry)
    word = models.ForeignKey(Word)
    count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('entry', 'word')

    def __unicode__(self):
        return u'%s - %s - %s' % (self.entry.title, self.word.word, self.count)


# Words API ===================================================================


class WordNotFound(Exception):
    def __init__(self, word):
        self.word = word

    def __str__(self):
        return "Word '%s' not found" % self.word


class FeedNotFound(Exception):
    def __init__(self, feed_link):
        self.feed_link = feed_link

    def __str__(self):
        return "Feed '%s' not found" % self.feed_link


class EntryNotFound(Exception):
    def __init__(self, entry_link):
        self.entry_link = entry_link

    def __str__(self):
        return "Entry '%s' not found" % self.entry_link


class WordError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class WordApi(object):
    def find(self, word, feed_link=None, entry_link=None):
        rv = {}
        try:
            if not word:
                raise WordError(u"Empty word. Specify a word.")
            word = word.lower()

            db_word = Word.objects.filter(word=word).first()
            if not db_word:
                raise WordError("Word '%s' not found" % word)

            result = OrderedDict()
            result['word'] = db_word.word

            # word count for feed_link
            if feed_link:
                feed = Feed.objects.filter(link=feed_link).first()
                if not feed:
                    raise FeedNotFound(feed_link)

                result['count'] = self._get_feed_word_count(feed_link, word)
                result['feed_link'] = feed_link

            # word count for entry_link
            elif entry_link:
                entry = Entry.objects.filter(link=entry_link).all()
                if not entry:
                    raise EntryNotFound(entry_link)

                result['count'] = self._get_entry_word_count(entry_link, word)
                result['entry_link'] = entry_link

            # word count for all feeds
            else:
                result['word'] = db_word.word
                result['count'] = db_word.count

            rv['result'] = result
        except (WordError, WordNotFound, FeedNotFound, EntryNotFound) as e:
            rv['error'] = str(e)
        return rv

    def _get_feed_word_count(self, feed_link, word):
        feed_word = FeedWord.objects.filter(word__word=word,
                                            feed__link=feed_link).first()
        count = 0
        if feed_word:
            count = feed_word.count
        return count

    def _get_entry_word_count(self, entry_link, word):
        entry_word = EntryWord.objects.filter(word__word=word,
                                              entry__link=entry_link).first()
        count = 0
        if entry_word:
            count = entry_word.count
        return count


# Feeder  =====================================================================


class Feeder(object):
    def __init__(self):
        self.parser = feedparser

    def process_feeds(self):
        feeds = Feed.objects.filter(is_active=True)
        for feed in feeds:
            logger.info('Processing feed: %s' % feed.link)
            self.process_feed(feed)
            logger.info('\n')

    def process_feed(self, feed):
        rss = self.parser.parse(feed.link, modified=feed.last_modified,
                                etag=feed.etag)
        if rss.feed:
            if 'status' in rss:
                logger.info('Status: %s' % rss.status)
            if 'etag' in rss:
                feed.etag = rss.etag
            if 'modified' in rss:
                modified = self.time_to_datetime(rss.modified_parsed)
                feed.last_modified = modified
            feed.title = rss.feed.title
            feed.save()
            for entry in rss.entries:
                self.process_entry(entry, feed)
        else:
            logger.info("Not modified, skipping: %s" % feed)

    def process_entry(self, entry, feed):
        title = ''
        title_words = []
        if 'link' in entry:
            link = entry.link
        if 'title' in entry:
            title = entry.title
            title_words = self.extract_words(title)

        content = ''
        content_words = []
        if 'content' in entry:
            for c in entry.content:
                if 'value' in c:
                    content_words.extend(self.extract_words(c.value))
                    content += c.value
        elif 'summary' in entry:
            content_words = self.extract_words(entry.summary)
            content = entry.summary

        words = content_words + title_words
        db_entry = Entry.objects.filter(link=link).first()
        is_new_entry = False
        if db_entry is None:
            db_entry = Entry(link=link, title=title, content=content)
            db_entry.save()
            is_new_entry = True
        self.save_words(words, db_entry, feed, is_new_entry)

    def time_to_datetime(self, time_struct):
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
    def save_words(self, words, entry, feed, is_new_entry):
        logger.info('Saving: %s words' % len(words))
        is_new_feed_entry = False
        if not Feed.objects.filter(pk=feed.pk, entries__pk=entry.pk).exists():
            feed.entries.add(entry)
            is_new_feed_entry = True
        for w in words:
            # increment words only if it's a new entry
            if is_new_entry:
                word, is_created = Word.objects.get_or_create(word=w)
                word.count += 1
                word.save()

            # increment feed word only if it's a feed's new entry
            if is_new_feed_entry:
                feed_word, is_created = FeedWord.objects.get_or_create(
                    feed=feed, word=word)
                feed_word.count += 1
                feed_word.save()

            # increment entry word only when it's a new entry
            if is_new_entry:
                entry_word, is_created = EntryWord.objects.get_or_create(
                    entry=entry, word=word)
                entry_word.count += 1
                entry_word.save()
