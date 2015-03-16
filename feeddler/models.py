from collections import OrderedDict
from django.db import models


class Feed(models.Model):
    """Feeds."""
    link = models.URLField(max_length=512, unique=True)
    is_active = models.BooleanField('Active', default=False)
    title = models.CharField(max_length=1024, blank=True, null=True)
    last_modified = models.DateTimeField(blank=True, null=True)
    etag = models.CharField(max_length=512, blank=True, null=True)
    words = models.ManyToManyField("Word", through='FeedWord')

    def __unicode__(self):
        return self.link


class Entry(models.Model):
    """Feed entries."""
    feed = models.ForeignKey(Feed)
    link = models.CharField(max_length=512, default='')
    title = models.CharField(max_length=512, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    words = models.ManyToManyField("Word", through='EntryWord')

    class Meta:
        unique_together = ('feed', 'link')

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
