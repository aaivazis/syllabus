from django.conf.urls import  url, include

from ..views.spaces import *

# calendar urls
urlpatterns = [
    url(r'(?i)^viewTimeline/$', viewTimeline),
    url(r'(?i)^viewAnnouncements/$', viewAnnouncements),
    url(r'(?i)^setSyllabus/$', setSyllabus),
    url(r'(?i)^viewSyllabus/$', viewSyllabus),

    # timeline urls
    url (r'(?i)^timeline/', include([
        url(r'(?i)^changeEventTitle/$', changeEventTitle),
        url(r'(?i)^changeEventDescription/$', changeEventDescription),
        url(r'(?i)^changeEventAssocReading/$', changeEventAssocReading),
    ])),
]