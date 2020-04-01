# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import connection, transaction
from django.shortcuts import render, render_to_response
from django.http import HttpResponse
import mysql.connector
from django.template import RequestContext
from student.models import *


class DB:

    def __init__(self):
        self.cursor = connection.cursor()

    def __del__(self):
        self.cursor.close()
        connection.close()

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


def sqlError(err):
    response = render_to_response(
        '404.html', {}, context_instance=RequestContext(err))
    response.status_code = 404
    return response


def home(request):
    database = DB()

    books_db = "select distinct b.title, b.barcode, t.DATE from books_db as b, transaction as t where b.barcode = t.barcode and t.cardnumber = '123' group by title;"
    query = "select distinct b.title, b.barcode, t.DATE " + "from books as b, transaction as t" + \
        " where b.barcode = t.barcode and t.cardnumber = '123' group by title union all " + books_db
    errorMsg = "Error in selecting from books_db or books"

    row = database.select(query, errorMsg)

    if not len(row):     # If no book is issued, return
        context = {
            'noBookIssued': True
        }
        return render(request, 'student/issue-history.html', context)

    result = []

    for i in row:

        temp = {}
        temp["title"] = str(i[0])
        temp["barcode"] = str(i[1])
        temp["DATE"] = str(i[2])

        query_get_rating = "select rating,valid from ratings where barcode = (select bt.barcode from bt_map bt where bt.title ='" + \
            temp["title"] + "' limit 1) and cardnumber = 123;"
        errorMsg = "Error in selecting rating from ratings"

        res = database.select(query_get_rating, errorMsg)

        temp["rating"] = res[0][0]
        temp["valid"] = res[0][1]

        result.append(temp)

    context = {
        'noBookIssued': False,
        'result': result
    }

    return render(request, 'student/issue-history.html', context)


def recommendLibrary(request):
    cursor = connection.cursor()
    query = ""
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

        for i in row:

            temp = {}
            temp["barcode"] = str(i[0])
            temp["title"] = str(i[1])

            if temp['barcode'].find("DB") > 0:      # barcode contains DB
                queryAuthor = "select author from books_db where barcode = '" + \
                    temp['barcode'] + "' ;"

            else:
                queryAuthor = "select author from books where barcode = '" + \
                    temp['barcode'] + "' ;"
            errorMsg = "Error in selecting author from books_db or books"

            author = database.select(queryAuthor, errorMsg)
            if not len(author):
                temp['author'] = "Not Available"

            else:
                temp['author'] = str(author[0][0])

            libraryResult.append(temp)

    if request.POST.get('checkRecommendedBooks'):
        searchBook = False
        checkRecommendedBooks = True
        newBookRecommendation = False
        newBookRecommended = False

        # hiddenTitle is temp, actually should be title
        hiddenTitle = request.POST.get("hiddenTitle")

        query = "select srNo, bookTitle, author, requestCount from libraryRecommendation where bookTitle like '%" + \
            hiddenTitle + "%' group by bookTitle;"
        errorMsg = "error in selecting from libraryRecommendation"

        row = database.select(query, errorMsg)

        for i in row:

            temp = {}
            temp["srNo"] = str(i[0])
            temp["title"] = str(i[1])
            temp["author"] = str(i[2])
            temp["requestCount"] = str(i[3])

            alreadyRecommendedResult.append(temp)

    if request.POST.get('newBookRecommendation'):

        hiddenTitle1 = request.POST.get('hiddenTitle1')

        newBookRecommendation = True
        searchBook = False
        checkRecommendedBooks = False
        newBookRecommendehiddenTitled = False

    if request.POST.get('newBookSubmit'):

        userCardnumber = "I2K16102102"

        newBookRecommendation = True
        searchBook = False
        checkRecommendedBooks = False
        newBookRecommended = True
        alreadyRequested = False

        newTitle = str(request.POST.get('newTitle')).lower()
        newAuthor = str(request.POST.get('newAuthor')).lower()
        newCategory = str(request.POST.get('newCategory')).lower()

        # check if same author and title already exists
        query = "select * from libraryRecommendation where bookTitle = '" + \
            newTitle + "' and author = '" + newAuthor + "';"
        errorMsg = "Error in selecting in libraryRecommendation"

        row = database.select(query, errorMsg)

        if not len(row):    # if does not exist, insert
            newRequest = True
            recommend = libraryRecommendation.objects.create(bookTitle=newTitle,
                                                             author=newAuthor,
                                                             category=newCategory,
                                                             requestCount=1)
            recommend.save()

            # Insert into bookRequest also

            getSrNo = "select max(srNo) from libraryRecommendation ;"
            errorMsg = "Error in selecting max srNo from libraryRecommendation"

            srNo = database.select(getSrNo, errorMsg)
            # print(str(srNo[0][0]))

            # Insert into bookRequest, denoting user has requested for book
            insertQuery = "insert into bookRequest (srNo, cardnumber) values ('" + str(
                srNo[0][0]) + "', '" + userCardnumber + "');"
            errorMsg = "Error in inserting bookRequest"

            insertSuccessful = database.insertOrUpdateOrDelete(
                insertQuery, errorMsg)

            if not insertSuccessful:
                alreadyRequested = True
                newRequest = False
                failMsg = "You have already requested for this book"

            if not failMsg:
                successMsg = "New Book Recommended"

        else:  # else update

            # Insert vote in bookRequest table cardnumber needed
            insertQuery = "insert into bookRequest (srNo, cardnumber) values ('" + str(
                row[0][0]) + "', '" + userCardnumber + "');"
            errorMsg = "Error in inserting bookRequest"

            insertSuccessful = database.insertOrUpdateOrDelete(
                insertQuery, errorMsg)

            if not insertSuccessful:
                alreadyRequested = True
                newRequest = False
                failMsg = "You have already requested for this book"

            if not alreadyRequested:  # Update requestCount
                updateQuery = "update libraryRecommendation set requestCount = requestCount + 1 where bookTitle = '" + \
                    newTitle + "' and author = '" + newAuthor + "';"
                errorMsg = "Error in updating libraryRecommndation"

                updateSucessful = database.insertOrUpdateOrDelete(
                    updateQuery, errorMsg)

                if not updateSucessful:
                    failMsg = "Error in updating requestCount"

            if not failMsg:
                successMsg = "New Book Recommended"

    if request.POST.get("increaseRequestCount"):

        userCardnumber = "I2K16102102"

        alreadyRequested = False
        newRequest = True
        newBookRecommended = True

        srNo = request.POST.get("increaseRequestCount")
        # Insert vote in bookRequest table cardnumber needed
        insertQuery = "insert into bookRequest (srNo, cardnumber) values ('" + \
            srNo + "', '" + userCardnumber + "');"
        errorMsg = "Error in inserting bookRequest"

        insertSuccessful = database.insertOrUpdateOrDelete(
            insertQuery, errorMsg)

        if not insertSuccessful:
            alreadyRequested = True
            newRequest = False
            failMsg = "You have already requested for this book"

        if not alreadyRequested:  # Update requestCount
            updateQuery = "update libraryRecommendation set requestCount = requestCount + 1 where bookTitle = '" + \
                newTitle + "' and author = '" + newAuthor + "';"
            errorMsg = "Error in updating libraryRecommndation"

            updateSucessful = database.insertOrUpdateOrDelete(
                updateQuery, errorMsg)

            if not updateSucessful:
                failMsg = "Error in updating requestCount"

        if not failMsg:
            successMsg = "New Book Recommended"

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

    cursor.close()
    connection.close()
    return render(request, 'student/recommend-library.html', context)


def studentRecommendation(request):

    result = []

    context = {
        'result': result
    }
    return render(request, 'student/recommend-student.html', context)
