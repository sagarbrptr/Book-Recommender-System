# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import connection, transaction
from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse
# import mysql.connector
from django.template import RequestContext

from .decorators import login_required_and_not_staff

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

from django.core.cache import cache
from django.views.decorators.cache import cache_page

import requests

class DB:

    def __init__(self):
        self.cursor = connection.cursor()

    def __del__(self):
        self.cursor.close()
        connection.close()

    def beginTransaction(self):

        try:
            self.cursor.execute("set autocommit = off;")
        except:
            print("Error in setting autocommit off")
            return False

        try:
            self.cursor.execute("begin;")
        except:
            print("Error in beginning transaction")
            return False

        return True

    def rollback(self):

        try:
            self.cursor.execute("rollback;")
        except:
            print("Error in rolling back")
            return False

        try:
            self.cursor.execute("set autocommit = on;")
        except:
            print("Error in setting autocommit on")
            return False

        return True

    def commit(self):

        try:
            self.cursor.execute("commit;")
        except:
            print("Error in commiting")
            return False

        try:
            self.cursor.execute("set autocommit = on;")
        except:
            print("Error in setting autocommit on")
            return False

        return True

    def select(self, query, errorMsg):
        try:
            self.cursor.execute(query)

        except:
            print(errorMsg)
            return False

        row = self.cursor.fetchall()
        return row

    def insertOrUpdateOrDelete(self, query, errorMsg):
        try:
            self.cursor.execute(query)
        except:
            print(errorMsg)
            return False

        return True

def combineDictionaries(a, b):
    result = []  
    i = 0
    while i < len(a):
        temp = {}
        temp["title"] = a[i]['title']
        temp["barcode"] = a[i]['barcode']
        temp["DATE"] = a[i]['DATE']
        temp['valid'] = b[i]['valid']
        temp['rating'] = b[i]['rating']

        result.append(temp)
        i += 1
    
    return result

def getRatings(bookInfo, userCardnumber, database = DB()):

    bookRating = []
    for i in bookInfo:
        title = i['title']
        temp = {}
        query_get_rating = "select rating,valid from ratings where barcode = (select bt.barcode from bt_map bt where bt.title ='" + \
                title + "' limit 1) and cardnumber = '" + \
                userCardnumber + "';"
        errorMsg = "Error in selecting rating from ratings"

        res = database.select(query_get_rating, errorMsg)

        if res:
            temp["rating"] = res[0][0]
            temp["valid"] = res[0][1]
        bookRating.append(temp)
    return bookRating

@login_required(login_url="/login")
@login_required_and_not_staff
def studentHome(request):  

    userCardnumber = ""
    if request.user.is_authenticated():
        userCardnumber = request.user.username

    # Check if studenetHomeCache id valid
    studenetHomeCache = cache.get("studenetHomeCache", "Not_Valid")

    if studenetHomeCache != "Not_Valid" and studenetHomeCache:

        # studenetHomeCache is valid
        # Check if noBookIssuedCache is valid
        noBookIssuedCache = cache.get("noBookIssuedCache", "Not_Valid")

        if noBookIssuedCache != "Not_Valid":

            # If noBookIssuedCache
            if noBookIssuedCache:
                context = {
                'noBookIssued': True
                }
                return render(request, 'student/issue-history.html', context)

            # Else check if validBookRatingCache            
            validBookRatingCache = cache.get("validBookRatingCache", "Not_Valid")
            bookInfo = cache.get("bookInfoCache", "Not_Valid")

            if validBookRatingCache != "Not_Valid" and bookInfo != "Not_Valid":
                
                bookRating = cache.get("bookRatingCache", "Not_Valid")                

                # If no valid Book Rating 
                # Get Book Rating again
                if ( not validBookRatingCache ) or ( bookRating == "Not_Valid") :
                    bookRating = getRatings(bookInfo, userCardnumber)
                    validBookRatingCache = cache.set("validBookRatingCache", True)
                
                context = {
                'noBookIssued': False,
                'result': combineDictionaries(bookInfo, bookRating)
                }

                return render(request, 'student/issue-history.html', context)
                    

            

    database = DB()

    query = "select distinct b.title, b.barcode, t.DATE " + "from books as b, transaction as t" + \
        " where b.barcode = t.barcode and t.cardnumber = '" + \
            userCardnumber + "' group by title; "
    errorMsg = "Error in selecting from books"
    # print(query)

    row = database.select(query, errorMsg)

    # If no book is issued, return
    if not len(row):    

        # Add in cache 
        cache.set("studenetHomeCache", True)
        cache.set("noBookIssuedCache", True)     
        context = {
            'noBookIssued': True
        }

        return render(request, 'student/issue-history.html', context)

    bookInfo = []
    bookRating = []    

    for i in row:

        temp = {}
        temp["title"] = str(i[0])
        temp["barcode"] = str(i[1])
        temp["DATE"] = str(i[2])        

        bookInfo.append(temp)            
    
    bookRating = getRatings(bookInfo, userCardnumber, database)

    # Add in Cache
    cache.set("studenetHomeCache", True)
    cache.set("validBookRatingCache", True)
    cache.set("noBookIssuedCache", False) 

    # Add book transaction info in cache
    cache.set("bookInfoCache", bookInfo)

    # Add book ratings in cache
    cache.set("bookRatingCache", bookRating)    

    context = {
        'noBookIssued': False,
        'result': combineDictionaries(bookInfo, bookRating)
    }

    return render(request, 'student/issue-history.html', context)

@login_required(login_url="/login")
@login_required_and_not_staff
def giveRating(request):    

    if request.method == "GET":
        # InValidate StudentHomeCache
        cache.set('validBookRatingCache', False)

        userCardNumber = ""
        if request.user.is_authenticated():
            userCardNumber = request.user.username
        if(request.GET['bookTitle'] == "" or request.GET['rating'] == ""):
            return HttpResponse("Missing arguments")
        bookTitle = request.GET['bookTitle']
        rating = request.GET['rating']
        database = DB()

        # Start Transaction
        database.beginTransaction()

        # Select barcode from bt_map to be updated in ratings
        query = "select barcode from bt_map where title ='"+bookTitle+"' limit 1;"
        errorMsg = "error in getting barcode from bt_map"

        row = database.select(query, errorMsg)

        # If Barcode Found, proceed
        if row:
            barcodeFromBtMap = row[0][0]
        # Else barcode not found, rollback
        else:
            database.rollback()
            return HttpResponse("Unsuccessful select!")

        # Update in ratings
        # query = "REPLACE INTO ratings(cardnumber,barcode,rating,valid,userSrNo) VALUES ( '" + \
            # userCardNumber + "' , '" + barcodeFromBtMap + "' ," + rating + ",1, (select SrNo from user where cardnumber = '" + userCardNumber + "'));"
        query = "update ratings set rating = '" + str(rating) + "', valid = 1 where barcode = '" + barcodeFromBtMap + "' and cardnumber = '" + userCardNumber + "';"
        errorMsg = "Ratings weren't processed into DB"

        row = database.insertOrUpdateOrDelete(query, errorMsg)

        # If updated, commit
        if row:
            database.commit()
            return HttpResponse("Success!")
        # Else error in update, rollback
        else:
            database.rollback()
            return HttpResponse("Unsuccessful!")
    return HttpResponse("Not proper request method")


def increaseRequestCount(database, request, userCardnumber, srNo):

    alreadyRequested = False
    newRequest = True
    failMsg = ""
    successMsg = ""

    # Check if user has already requested the book
    # By inserting in bookRequest table directly
    # If inserted, then not requested earlier, otherwise requested

    # Insert vote in bookRequest table cardnumber needed
    insertQuery = "insert into bookRequest (srNo, cardnumber) values ('" + \
        srNo + "', '" + userCardnumber + "');"
    errorMsg = "Error in inserting bookRequest"

    insertSuccessful = database.insertOrUpdateOrDelete(
        insertQuery, errorMsg)

    # If insertion failed, rollback
    if not insertSuccessful:
        alreadyRequested = True
        newRequest = False
        failMsg = "You have already requested for this book"
        database.rollback()

    # Else if insertion successful, update requestCount in libraryRecommendation
    if not alreadyRequested:  # Update requestCount
        updateQuery = "update libraryRecommendation set requestCount = requestCount + 1 where srNo = '" + srNo + "';"
        errorMsg = "Error in updating libraryRecommndation"

        updateSucessful = database.insertOrUpdateOrDelete(
            updateQuery, errorMsg)

        # If update not successful, rollback
        if not updateSucessful:
            failMsg = "Error in updating requestCount"
            database.rollback()

    # If nothing failed, commit
    if not failMsg:
        successMsg = "New Book Recommended"
        database.commit()

    return alreadyRequested, newRequest, failMsg, successMsg


@login_required(login_url="/login")
@login_required_and_not_staff
def recommendLibrary(request):

    userCardnumber = ""
    if request.user.is_authenticated():
        userCardnumber = request.user.username

    libraryResult = []
    title = ""
    searchBook = True
    blankSearch = True
    alreadyRecommendedResult = []  # Turns on if user checks already recommended books
    checkRecommendedBooks = False
    newBookRecommendation = False  # Turns on when user wants to recommend new book
    newBookRecommended = False
    newTitle = ""
    newAuthor = ""
    newCategory = ""
    hiddenTitle = ""  # Needs to be fixed
    hiddenTitle1 = ""  # Needs to be fixed
    newRequest = "False"
    alreadyRequested = "False"
    successMsg = ""
    failMsg = ""

    database = DB()

    if request.POST.get('title'):
        searchBook = False
        blankSearch = False
        checkRecommendedBooks = False
        newBookRecommendation = False
        newBookRecommended = False

        title = request.POST.get('title')

        queryBooks = "select barcode, title from bt_map where title like '%" + \
            title + "%' group by title;"
        errorMsg = "Error in selecting from bt_map"

        row = database.select(queryBooks, errorMsg)

        # If there exists any row, iterate
        if row:
            for i in row:

                temp = {}
                temp["barcode"] = str(i[0])
                temp["title"] = str(i[1])

                queryAuthor = "select author from books where barcode = '" + \
                    temp['barcode'] + "' ;"
                errorMsg = "Error in selecting author from books_db or books"

                author = database.select(queryAuthor, errorMsg)
                if not author:
                    temp['author'] = "Not Available"

                else:
                    temp['author'] = str(author[0][0])

                libraryResult.append(temp)

    if request.POST.get('checkRecommendedBooks'):   # Check already Recommended books
        searchBook = False
        checkRecommendedBooks = True
        newBookRecommendation = False
        newBookRecommended = False

        # hiddenTitle is temp, actually should be title
        hiddenTitle = request.POST.get("hiddenTitle")

        query = "select srNo, bookTitle, author, requestCount from libraryRecommendation where bookTitle like '%" + \
            hiddenTitle + "%' group by bookTitle, author;"
        errorMsg = "error in selecting from libraryRecommendation"

        row = database.select(query, errorMsg)

        # If any row, iterate
        if row:
            for i in row:

                temp = {}
                temp["srNo"] = str(i[0])
                temp["title"] = str(i[1])
                temp["author"] = str(i[2])
                temp["requestCount"] = str(i[3])

                alreadyRecommendedResult.append(temp)

    if request.POST.get('newBookRecommendation'):   # Recommend new book

        hiddenTitle1 = request.POST.get('hiddenTitle1')

        newBookRecommendation = True
        searchBook = False
        checkRecommendedBooks = False

    if request.POST.get('newBookSubmit'):   # New book info is submitted

        newBookRecommendation = True
        searchBook = False
        checkRecommendedBooks = False
        newBookRecommended = True
        alreadyRequested = False

        newTitle = str(request.POST.get('newTitle')).lower()
        newAuthor = str(request.POST.get('newAuthor')).lower()
        newCategory = str(request.POST.get('newCategory')).lower()

        # Start Transaction
        database.beginTransaction()

        # check if same author and title already exists
        query = "select * from libraryRecommendation where bookTitle = '" + \
            newTitle + "' and author = '" + newAuthor + "';"
        errorMsg = "Error in selecting in libraryRecommendation"

        row = database.select(query, errorMsg)

        if row:
            if not len(row):    # does not exists,  new Book is recommended
                newRequest = True

                #insert in libraryRecommendation
                insertQuery = "insert into libraryRecommendation values(default, '" + \
                    newTitle + "', '" + newAuthor + "', '" + newCategory + "', 1);"
                errorMsg = "Error in inserting in libraryRecommendation"

                # If insert in libraryRecommendation sucessful,
                # select latest srNo of book inserted
                if database.insertOrUpdateOrDelete(insertQuery, errorMsg):

                    getSrNo = "select max(srNo) from libraryRecommendation ;"
                    errorMsg = "Error in selecting max srNo from libraryRecommendation"

                    latestSrNo = database.select(getSrNo, errorMsg)

                    # If valid srNo found, insert in bookRequest
                    if latestSrNo:
                        srNo = str(latestSrNo[0][0])
                        insertQuery = "insert into bookRequest (srNo, cardnumber) values ('" + \
                            srNo + "', '" + userCardnumber + "');"
                        errorMsg = "Error in inserting bookRequest"

                        insertSuccessful = database.insertOrUpdateOrDelete(
                            insertQuery, errorMsg)

                        # If insertion failed, rollback
                        if not insertSuccessful:
                            alreadyRequested = True
                            newRequest = False
                            failMsg = "Error in insertion in bookRequest"
                            database.rollback()

                        # Else insertion was successful, commit
                        if not failMsg:
                            successMsg = "New Book Recommended Successfully"
                            database.commit()

                    # Else error in srNo, rollback
                    else:
                        print("Error in selecting srNo from libraryRecommendation")
                        failMsg = "Error in selecting srNo from libraryRecommendation"
                        database.rollback()

                # Else error in insertion in libraryRecommendation
                else:
                    print("Error in insertion in libraryRecommendation")
                    failMsg = "Error in inserting libraryRecommendation"
                    database.rollback()

            # Else book already exists, increase count
            else:
                srNo = str(row[0][0])
                alreadyRequested,  newRequest, failMsg, successMsg = increaseRequestCount(
                    database, request, userCardnumber, srNo)

        else:
            failMsg = "Error in title. Check if you have not inserted any quotes!! (-_-)"

    if request.POST.get("increaseRequestCount"):
        newBookRecommended = True
        srNo = request.POST.get("increaseRequestCount")

        database.beginTransaction()

        alreadyRequested,  newRequest, failMsg, successMsg = increaseRequestCount(
            database, request, userCardnumber, srNo)

    context = {
        'searchBook': searchBook,
        'libraryResult': libraryResult,
        'blankSearch': blankSearch,
        'alreadyRecommendedResult': alreadyRecommendedResult,
        'checkRecommendedBooks': checkRecommendedBooks,
        'newBookRecommendation': newBookRecommendation,
        'newTitle': newTitle,
        'newAuthor': newAuthor,
        'newCategory': newCategory,
        'newBookRecommended': newBookRecommended,
        'title': title,
        'alreadyRequested': alreadyRequested,
        'newRequest': newRequest,
        'failMsg': failMsg,
        'successMsg': successMsg,
        'hiddenTitle': hiddenTitle,     # Needs to be fixed
        'hiddenTitle1': hiddenTitle1
    }
    return render(request, 'student/recommend-library.html', context)


@login_required(login_url="/login")
@login_required_and_not_staff
@cache_page(60 * 15)
def studentRecommendation(request):
    
    context = {
        'result' : "Hello",
    }
    return render(request, 'student/recommend-student.html', context)


@login_required(login_url="/login")
@login_required_and_not_staff
def userProfile(request):
    database = DB()
    passwordChanged = False
    passwordSubmit = False
    failMsg = ""
    user = ""

    if request.POST.get('changePassword'):
        passwordSubmit = True

        # Get current cardNumber
        userCardnumber = ""
        if request.user.is_authenticated():
            userCardnumber = request.user.username

        # Get user from django user model
        try:
            user = User.objects.get(username=userCardnumber)

        except:
            failMsg = "Error in retrieving user object from django user model"

        if user:
            oldPassword = request.POST.get("oldPassword")
            newPassword = request.POST.get("newPassword")

            # Start Transaction
            database.beginTransaction()

            # If old password is correct, update new Password
            if user.check_password(oldPassword):

                # Update in db
                updateQuery = "update user set password = '" + newPassword + \
                    "' where cardnumber = '" + userCardnumber + "';"
                errorMsg = "Error in updating password in database"

                # If update in db successful, update in django
                if database.insertOrUpdateOrDelete(updateQuery, errorMsg):

                    # Update in django user model
                    try:
                        user.set_password(newPassword)
                        user.save()

                        passwordChanged = True
                        messages.add_message(
                            request, messages.INFO, "Password has been Changed Successfully. Please Login again")
                        return redirect("/login")

                    # Error in updating in django
                    except:
                        failMsg = "Error in updating password"
                        database.rollback()

                # Else, error in updating in db rollback
                else:
                    failMsg = "Error in updating password"
                    database.rollback()

            # Else, old password is wrong
            else:
                failMsg = "Old Password is not correct"
                database.rollback()

    context = {
        "passwordSubmit": passwordSubmit,
        "passwordChanged": passwordChanged,
        "failMsg": failMsg,
    }
    return render(request, 'student/user-profile.html', context)

