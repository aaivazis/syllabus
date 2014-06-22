from rest_framework import generics, permissions
from django.http import HttpResponse, HttpResponseBadRequest

from .serializers import (ClassSerializer, SectionSerializer, EventSerializer, 
                          GradebookSerializer, GradingScaleSerializer, WeightSerializer, 
                          CalendarSerializer)

from ..models import Class, Section, Event, GradingScale, Weight

from ...core.models import SyllUser, MetaData

import django, datetime

# return all of the classes
class ClassList(generics.ListCreateAPIView):
    model = Class
    serializer_class = ClassSerializer
    permission_classes = [
        permissions.AllowAny
    ]


# return the weights of a class
class WeightsList(generics.RetrieveUpdateDestroyAPIView):
    model = Weight
    serializer_class = WeightSerializer
    permission_classes = [
        permissions.AllowAny
    ]

    # return the classes that the user teachers
    def get_object(self):
        return Class.objects.get(pk = self.kwargs.get('pk')).weights

# return the classes taught by the user
class ClassesTaughtByMe(generics.ListCreateAPIView):
    model = Class
    serializer_class = ClassSerializer
    permission_classes = [
        permissions.AllowAny
    ]

    # return the classes that the user teachers
    def get_queryset(self):
        return Class.objects.filter(professor = self.request.user)

# return the data necessary for a gradebook (read-only)
class Gradebook(generics.RetrieveAPIView):
    model = Class
    serializer_class = GradebookSerializer
    permission_classes = [
        permissions.AllowAny
    ]

    # return the requested class
    def get_object(self):
        return Class.objects.get(pk = self.kwargs.get('pk'))

class GradingScale(generics.RetrieveUpdateDestroyAPIView):
    """ return the grading scale for a given class """
    model = GradingScale
    serializer_class = GradingScaleSerializer
    permission_classes = [
        permissions.AllowAny
    ]

    def get_object(self):
        """ return the grading scale for a given class """
        return Class.objects.get(pk = self.kwargs.get('pk')).gradingScale

# return all of the sections
class SectionList(generics.ListCreateAPIView):
    model = Section
    serializer_class = SectionSerializer
    permission_classes = [
        permissions.AllowAny
    ]

# return all of the events in a class
class ClassEventList(generics.ListCreateAPIView):
    model = Event
    serializer_class = EventSerializer
    permission_classes = [
        permissions.AllowAny
    ]

    # return the events from the requested class
    def get_queryset(self):
        return Class.objects.get(pk = self.kwargs.get('pk')).events.all()

# return all of the homework events that are before and including tomorrow
class HomeworkByClass(generics.ListCreateAPIView):
    model = Event
    serializer_class = EventSerializer
    permission_classes = [
        permissions.AllowAny
    ]

    def get_queryset(self):
        return (Event.objects.filter(classes__id=self.kwargs.get('id'))
                .exclude(category='lecture')
                .exclude(category='meeting')
                .filter(date__lte = django.utils.timezone.now() + datetime.timedelta(days = 1)))

# return the calendar of the current user
class MyCalendar(generics.RetrieveAPIView):
    model = SyllUser
    serializer_class = CalendarSerializer
    permission_classes = [
        permissions.AllowAny
    ]

    # return the classes that the user teachers
    def get_object(self):
        return self.request.user


class RetrieveEvent(generics.RetrieveUpdateDestroyAPIView):
    """ the CRUD interface for syllabus events """
    model = Event
    serializer_class = EventSerializer
    permission_classes = [
        permissions.AllowAny
    ]

    # return the event specified by the url
    def get_object(self):
        return Event.objects.get(pk = self.kwargs.get('pk'))

class CreateEvent(generics.CreateAPIView):
    """ create an event """
    model = Event
    serializer_class = EventSerializer
    permission_classes = [
        permissions.AllowAny
    ]

    # handle the creation of an event to add various meta data
    def create(self, *args, **kwargs):

        # grab the posted data
        data = self.request.DATA
        
        # check that the necessary data is here
        if ('title' not in data or 'description' not in data or 'date' not in data or 
            'time' not in data or 'category' not in data or 'classes' not in data):
            return HttpResponseBadRequest 

        # create the event
        event = Event()
        event.title = data['title']
        event.description = data['description']
        event.date = data['date']
        event.time = data['time']
        event.category = data['category']
        event.save()

        # add the possiblePoints metaData
        if 'possiblePoints' in data:
            # create the metaData entry
            meta = MetaData()
            meta.key = 'possiblePoints'
            meta.value = data['possiblePoints']
            meta.save()

            # add the metaData to the entry
            event.metaData.add(meta)

        # add the sub category
        if 'category' in data:
            # create the metaData entry
            meta = MetaData()
            meta.key = 'subCategory'
            meta.value = data['category']
            meta.save()

            # add the metaData to the entry
            event.metaData.add(meta)

        # for each class that this event belongs to
        for pk in data['classes']:
            # add the event to the class
            Class.objects.get(pk=pk).events.add(event)
            
        return HttpResponse(event.id)
