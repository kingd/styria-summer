from django.conf.urls import patterns, url

from feeddler import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^words/$', views.words_api, name='words_api'),
    url(r'^feed-activity/$', views.feed_activity, name='feed_activity'),
    url(r'^add-feed/$', views.add_feed, name='add_feed'),
    url(r'^top-words/$', views.top_words, name='top_words'),
)
