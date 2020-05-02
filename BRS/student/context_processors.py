from __future__ import unicode_literals
from django.db import connection, transaction
from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import RequestContext
import random
from django.contrib.admin.views.decorators import staff_member_required

from django.core.cache import cache
from django.views.decorators.cache import cache_page

from . views import DB

# @cache_page(60 * 30)
def userInfo(request):
    
    userClass = ""
    userGender = ""
    userName = ""
    userRollNo = ""
    userEmail = ""
    userCardnumber = ""

    database = DB()
    
    if request.user.is_authenticated():
        userCardnumber = request.user.username

    getUserInfo = "select * from user where cardnumber = '" + userCardnumber + "';"
    errorMsg = "Error in getting user info"

    row = database.select(getUserInfo, errorMsg)

    if row:
        userRollNo = row[0][2]
        userName = row[0][3]
        userGender = row[0][4]
        userClass = row[0][5]
        userEmail = row[0][6]

    context = {
        'userCardnumber' : userCardnumber,        
        'userRollNo' : userRollNo,
        'userName' : userName,
        'userGender' : userGender,
        'userClass' : userClass,
        'userEmail' : userEmail,
    }

    return context