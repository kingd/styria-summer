from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib import messages

from feeddler.models import Feed
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
    """Adds a new feed."""
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
