# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from .models import ratings

admin.site.register(ratings)
# Add any other table here to see all the entries in django admin portal