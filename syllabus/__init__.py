# this file represents common imports among all of the views

from django.shortcuts import HttpResponseRedirect, HttpResponse #, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import jinja2
from compressor.contrib.jinja2ext import CompressorExtension
from jinja2 import Environment, FileSystemLoader

import re

from django.conf import settings
from django.template.loader import get_template
from django.template import Context
from django.core.servers.basehttp import FileWrapper
import calendar, os, mimetypes, zipfile, tempfile
from collections import defaultdict
import datetime, collections, time

from re import escape
from collections import defaultdict, OrderedDict

from datetime import date

template_dirs = getattr(settings,'TEMPLATE_DIRS')
default_mimetype = getattr(settings, 'DEFAULT_CONTENT_TYPE')
env = Environment(loader=FileSystemLoader(template_dirs), extensions=['jinja2.ext.with_','jinja2.ext.do', CompressorExtension])
env.globals['perms']=settings.PERMS

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

def nl2br(value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') for p in _paragraph_re.split(escape(value)))
    return result

env.filters['linebreaks'] = nl2br

dayDict = {
    '1':'M',
    '2':'T',
    '3':'W',
    '4':'Th',
    '5':'F',
    '6':'Sat',
    '7':'Sun'
}


def render_to_response(filename, context={},mimetype=default_mimetype):
    template = env.get_template(filename)
    rendered = template.render(**context)
    return HttpResponse(rendered,mimetype=mimetype)
