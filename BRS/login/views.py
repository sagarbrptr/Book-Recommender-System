# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import connection, transaction
from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse
from django.template import RequestContext
from django.core.cache import cache

# from student.models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from student.views import DB


def validate_user(username, password):
    database = DB()
    query = "select * from user where cardnumber = '" + \
        username+"' and password = '"+password+"';"
    print(query)
    err = "invalid credentials"

    row = database.select(query, err)
    if(len(row) == 0):
        return 0
    else:
        return 1


def loginview(request):
    # always logout when redirected to login
    logout(request)

    passwordChanged = False
    loginFailed = False
    user = ""

    if request.method == "POST":
        # if request.POST.get("login")
        username = str(request.POST.get('username'))
        password = str(request.POST.get('pass'))

        # Check If user is already created
        try:
            user = User.objects.get(username=username)

        # Else validate user and create user
        except User.DoesNotExist:
            if validate_user(username, password):
                user = User.objects.create_user(username, 'a@b.com', password)

                login(request, user)
                return redirect("/studentHome")

            else:
                loginFailed = True

        if user:
            # If user is created
            # Check password
            if user.check_password(password):
                login(request, user)

                # Check if librarian or not
                if user.is_staff:
                    return redirect("/librarianHome") 
                else:
                     cache.set('userCardNumber', username)
                     return redirect("/studentHome")                     


            else:
                loginFailed = True

    context = {
        "passwordChanged" : passwordChanged,
        "loginFailed": loginFailed
    }
    return render(request, 'login/login.html', context)


def logoutview(request):    

    # Clear cache
    cache.clear()
    cache.delete('username')

    logout(request)
    return redirect("/login")

def notStaff(request):
    return HttpResponse("Not authorized")
