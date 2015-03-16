from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib import messages

from feeddler.models import Feed, WordApi
from feeddler.forms import FeedForm


def index(request):
    """Lists all feeds."""
    feeds = Feed.objects.all()
    context = {
        'feeds': feeds
    }
    return render(request, 'feeddler/index.html', context)


def feed_activity(request):
    """Toggles feed activity flag. Input parameter: `feed_id`."""
    context = {}
    if request.method == 'POST':
        try:
            feed = Feed.objects.get(pk=request.POST['feed_id'])
            feed.is_active = not feed.is_active
            feed.save()
            context['result'] = str(feed.is_active).capitalize()
            context['is_active'] = feed.is_active
            success = True
        except Feed.DoesNotExist:
            success = False
    context['success'] = success
    return JsonResponse(context)


def add_feed(request):
    """Adds new feed."""
    if request.method == 'POST':
        form = FeedForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, 'Success.')
            return HttpResponseRedirect(reverse('add_feed'))
    else:
        form = FeedForm()
    context = {
        'form': form,
    }
    return render(request, 'feeddler/add_feed.html', context)


def words_api(request):
    """
    Words API.

    :param word: Word to count - Required
    :param feed_link: Count `word` in feed_link
    :param entty_link: Count `word` in entry_link

    If `feed_link` is provided, counts the `word` only in that feed.
    If `entry_link` is provided, counts the `word` only in that entry.

    Results on success::
        # only word param
        {
            'result': {
                'word': 'exampleword',
                'count' 12
            }
        }

        # word and feed_link params
        {
            'result': {
                'word': 'exampleword',
                'count' 12,
                'feed_link': 'somelink'
            }
        }

        # word and entry_link params
        {
            'result': {
                'word': 'exampleword',
                'count' 12,
                'entry_link': 'somelink'
            }
        }

    Result on error::
        {
            'error': 'Some error message'
        }
    """
    word = request.GET.get('word')
    feed_link = request.GET.get('feed_link')
    entry_link = request.GET.get('entry_link')
    word_api = WordApi()
    rv = word_api.find(word, feed_link=feed_link, entry_link=entry_link)
    return JsonResponse(rv)
