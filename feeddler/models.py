from django.db import models


class Feed(models.Model):
    """Feeds."""
    link = models.URLField(max_length=512, unique=True)
    is_active = models.BooleanField('Active', default=False)
    title = models.CharField(
        max_length=1024, blank=True, null=True, editable=False)
    last_build_date = models.DateTimeField(
        blank=True, null=True, editable=False)

    def __unicode__(self):
        return '{0}: {1}'.format(self.link, self.is_active)
