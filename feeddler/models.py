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
            return 'No title'
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
