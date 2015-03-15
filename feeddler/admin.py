from django.contrib import admin
from feeddler.models import Feed, Entry, Word, FeedWord, EntryWord

admin.site.register(Feed)
admin.site.register(Entry)
admin.site.register(Word)
admin.site.register(FeedWord)
admin.site.register(EntryWord)
