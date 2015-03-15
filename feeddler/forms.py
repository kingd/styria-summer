from django.forms import ModelForm

from feeddler.models import Feed


class FeedForm(ModelForm):
    class Meta:
        model = Feed
        fields = ['link', 'is_active']
