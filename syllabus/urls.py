# -*- Python -*-
# -*- coding: utf-8 -*-
#
# alec aivazis
#
# this file describes the primary url router for syllabus

# django imports
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

# import the syllabusapplications
from .views import Home


# define the primary url patterns
urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'', Home.as_view()),
    # add the static urls
) 

# if the debug flag is on
if settings.DEBUG:
    # add the local static url configuration
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# end of file
