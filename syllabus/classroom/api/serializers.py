##
# Serializers for classroom api
#
##
# system imports
import django, datetime
from rest_framework import serializers
# syllabus imports
from ...core.models import Upload
from ...core.models import SyllUser as User
from ..models import (Class, Event, Section, Grade, GradingScale, GradingCategory,
                      Weight, WeightCategory)

from ...classroom.models import State
from ...academia.models import Term

from ...core.fields import MetaDataField

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        """ meta class for SectionSerializer """
        model = Section
        fields = ('id', 'name' )

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        """ meta class for ClassSerializer """
        model = Class
        fields = ('id', 'name', 'sections')

    # the class sections as a list of id's
    sections = serializers.SerializerMethodField('getSections')
    # the name of the class
    name = serializers.SerializerMethodField('getName')
    
    def getName(self, obj):
        """return the name of the class"""
        return obj.profile.interest.abbrv + " " + str(obj.profile.number)

    # the categories in a weight group
    def getSections(self, obj):
        """ return serialized versions of the section"""
        sections = obj.sections.all()
        serializer = SectionSerializer(sections)
        return serializer.data

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        """ meta class for EventSerializer """
        model = Event
        fields = ('id', 'possiblePoints', 'title', 'category', 'type', 'weight',
                  'date', 'time','description', 'classes')

    category = MetaDataField(name="subCategory")
    possiblePoints = MetaDataField(name="possiblePoints")
    type = serializers.CharField(source="category")
    weight = serializers.SerializerMethodField('getWeight')

    def getWeight(self, obj):
        """ return the current weight of the event """
        return obj.calculateWorth()


class HomeworkSerializer(serializers.ModelSerializer):
    class Meta:
        """ meta class for HomeworkSerializer """
        model = Event
        fields = ('id', 'possiblePoints', 'title', 'category', 'date', 'time',
                  'description', 'classes', 'status' )

    category = MetaDataField(name="subCategory")
    possiblePoints = MetaDataField(name="possiblePoints")
    type = serializers.CharField(source="category")
    classes = serializers.SerializerMethodField('getClassNames')
    status = serializers.SerializerMethodField('getStatus')

    def getWeight(self, obj):
        """ return the current weight of the event """
        return obj.calculateWorth()

    def getClassNames(self, obj):
        """ return a list of the names that this event is a member of """
        classNames = []
        # for each class that this user is a student in
        for klass in Class.objects.byEvent(obj):
            # add the name to the list
            classNames.append(klass.getTitle())

        # return the list
        return classNames
       
    def getStatus(self, obj):
        """ return the most recent status of the event """
        # store the current user
        user =  self.context['request'].user
        # grab the most recent state
        state = State.objects.filter(event = obj).filter(user = user).order_by('-date')
        # if there is a state
        if state:
            # return its status
            return state[0].status
        # otherwise
        else:
            # return a blank string
            return ''
            

class WeightCategorySerializer(serializers.ModelSerializer):
    class Meta:
        """ meta class for WeightCategorySerializer """
        model = WeightCategory
        fields = ( 'category', 'percentage')

class WeightSerializer(serializers.ModelSerializer):
    class Meta:
        """ meta class for WeightSerializer """
        model = Weight
        fields = ('name', 'categories')

    # the categories in a weight group
    categories = serializers.SerializerMethodField('getCategories')

    def getCategories(self, obj):
        """ return serialized versions of the weights categories """
        categories = obj.categories.all().order_by('-percentage')
        serializer = WeightCategorySerializer(categories)
        return serializer.data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        """ meta class for UserSerializer """
        model = User
        fields = ('name', 'id')

    # the name of the user
    name = serializers.SerializerMethodField('getName')

    def getName(self, obj):
        """ return the name of the user """
        return obj.first_name + ' ' + obj.last_name

class UserGradeSerializer(serializers.ModelSerializer):
    """ collect the grades and graduation information of the user """
    class Meta:
        model = User
        fields = ('requirements', 'grades')

    requirements = serializers.SerializerMethodField('getRequirements')
    grades = serializers.SerializerMethodField('getGrades')

    def getRequirements(self, obj):
        """ return the graduation requirements of the user being serialized """
        return "hello"

    def getGrades(self, obj):
        """ return a summary of all of the grades for the user """
        data = []
        # go over every class
        for c in Class.objects.filter(sections__students = obj):
            # save the term
            term = c.term
            # and the grade
            grade = c.totalGrade(obj.pk)
            # collect the data
            data.append({
                'name' : c.getTitle(),
                'grade': {
                    'letter': grade[0],
                    'score': grade[1]
                },
                'term': {
                    'name': term.name,
                    'start': term.start
                }
            })

        # return the serialized data
        return data

class GradebookSerializer(serializers.ModelSerializer):
    class Meta:
        """ meta class for GradebookSerializer """
        model = Class
        fields = ('breadcrumb', 'events', 'gradebook', 'students')

    # the meta data of students in the class
    students = serializers.SerializerMethodField('getStudents')
    # the meta data of gradable events in the class
    events = serializers.SerializerMethodField('getGradableEvents')
    # the gradebook dictionary of {student} -> {event} -> {grade}
    gradebook = serializers.SerializerMethodField('getGradebook')
    # get the breadcrumb
    breadcrumb = serializers.SerializerMethodField('getBreadcrumb')

    def getStudents(self, obj):
        """ return the students in the serialized class """
        # save the data as a list of dictionarys
        data = []
        # get the users who are in the class
        users = User.objects.filter(classes__pk = obj.pk)
        # for each user
        for user in users:
            userDict = {
                "name" : user.first_name + ' ' + user.last_name,
                "id" : user.pk
            }
            # grab the grade data
            grade = obj.totalGrade(user.id)
            # if its valid
            if grade != -1:
                # add it to the return data
                userDict["totalGrade"] = {
                        "letter" : grade[0],
                        "score" : grade[1]
                }
            else:
                # else add -1
                userDict["totalGrade"] = '-1'
            
            data.append(userDict)
        
        # return the serialized data
        return data

    def getGradableEvents(self, obj):
        """ return the events that are gradable """
        # serialize the gradable events
        serializer = EventSerializer(obj.getGradableEvents())
        # return the serialized data
        return serializer.data

    def getGradebook(self, obj):
        """ return a dictionary of students pointing another dict
            of events to gradebook data """
        # gradebook is a dictionary of dictionaries
        gradebook = {}
        # the first level of keys correspond to the id of the student
        for student in User.objects.filter(classes__pk = obj.pk):
            gradebook[student.pk] = {}
            # the second level is the event
            for event in obj.getGradableEvents():
                gradebook[student.pk][event.pk] = {}
                
                # get the grades associated with this student/event
                grade = Grade.objects.filter(student = student).filter(event = event)
                # if there is a grade save it, otherwise use an empty string
                gradebook[student.pk][event.pk]['grade'] = grade[0].score if grade else ''

                # get the uploads
                uploads = Upload.objects.filter(event = event).filter(user = student).count()
                # if there are uploads, set it to true otherwise false
                gradebook[student.pk][event.pk]['hasUploads'] = True if uploads else False
                
                # set the onTime
                gradebook[student.pk][event.pk]['onTime'] = event.isStudentOnTime(student)
                

        return gradebook

    def getBreadcrumb(self, obj):
       return [obj.profile.interest + ' ' + str(obj.profile.number)] 

class GradingCategorySerializer(serializers.ModelSerializer):
    class Meta:
        """ meta class for GradingCategorySerializer """
        model = GradingCategory
        fields = ("lower", "value")

class GradingScaleSerializer(serializers.ModelSerializer):
    class Meta:
        """ meta class for GradingScaleSerializer """
        model = GradingScale
        fields = ('name', 'categories')

    categories = serializers.SerializerMethodField('getCategories')

    def getCategories(self, obj):
       """ return a serialization of the categories for this scale""" 
       categories = obj.categories.all().order_by('-lower')
       serializer = GradingCategorySerializer(categories)
       return serializer.data

    def restore_object(self, attrs, instance=None):
        """
        Given a dictionary of deserialized field values, either update
        an existing model instance, or create a new model instance.
        """
        if instance is not None:
            instance.name = attrs.get('name', instance.name)
            instance.categories = attrs.get('categories', instance.categories)
            return instance
        return GradingScale(**attrs)
       
class UserClassSchedule(serializers.ModelSerializer):
    """ return the classes and sections of the serialized user """
    class Meta:
        """ meta class for a user schedule """
        model = User
        fields = ('classes', 'sections', 'terms')

    classes = serializers.SerializerMethodField('getClasses')
    sections = serializers.SerializerMethodField('getSections')
    terms = serializers.SerializerMethodField('getTerms')

    def getTerms(self, obj):
        """ return the terms in which the user has sections """

        # grab the requested term
        GET =  self.context['request'].GET
        # if they asked for a specific term
        if 'name' in GET and 'year' in GET and GET['name'] and GET['year']:
            term = Term.objects.filter(start__year = GET['year']).get(name = GET['name'])
        else:
            term = Term.objects.getCurrentTerm()

        data = []
        # for every term with a section that has this `student
        for term in Term.objects.filter(classes__sections__students = obj):
            # serialize the term
            data.append({
                'name': term.name,
                'start': term.start,
                'end': term.end
            })

        # return the serialized data
        return {
            'selected': term.name + ' ' + str(term.start.year),
            'list': data,
        }

    def getClasses(self, obj):
        """ return the actual classes that the user is a part of """

        # grab the requested term
        GET =  self.context['request'].GET
        # if they asked for a specific term
        if 'name' in GET and 'year' in GET and GET['name'] and GET['year']:
            term = Term.objects.filter(start__year = GET['year']).get(name = GET['name'])
        else:
            term = Term.objects.getCurrentTerm()

        data = []
        # for every class that this user is a member of
        for c in Class.objects.filter(sections__students = obj):
            # for each meeting time
            for time in c.times.all():
                # serialize the timeslots
                data.append({
                    'name': c.profile.interest.abbrv + " " + str(c.profile.number),
                    'day': time.day,
                    'start': time.start,
                    'end': time.end
                })

        # return the data
        return data
        

    def getSections(self, obj):
        """ return the sections that this user is a member of """
        data = []
        # for each section that the user is a member of
        for section in Section.objects.filter(students = obj):
            # for each different time that this section occurs
            for time in section.times.all():
                # serialize the timeslots
                data.append({
                    'name': section.name,
                    'day': time.day,
                    'start': time.start,
                    'end': time.end
                })

        # return the 'serialized' data
        return data

class CalendarSerializer(serializers.ModelSerializer):
    class Meta:
        """ meta class for the calendar """
        model = User
        fields = ('assigned', 'classes')
        
    assigned = serializers.SerializerMethodField('getAssignedEvents')
    classes = serializers.SerializerMethodField('getClasses')

    def getClasses(self, obj):
        """ return the classes that are taught by the user """
        classes = []
        # for each class the user is teaching
        for c in obj.classesTeaching.all():
            # build the serialized data
            classes.append({
                'id': c.pk,
                'name': c.profile.interest.abbrv + ' ' + str(c.profile.number)
            })
        # return the data
        return classes

    def getAssignedEvents(self, obj):
        """ return the events that were assigned by the user """
        # keep the events in a list
        events = []
        # for each class that I teach
        for c in obj.classesTeaching.all():
            # for each of the gradable events
            for event in c.getGradableEvents():
                # serialize the event
                serialized = EventSerializer(event)
                # add it to the list
                events.append(serialized.data)

        # return the list
        return events
