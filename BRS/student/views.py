# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import connection, transaction
from django.shortcuts import render, render_to_response
from django.http import HttpResponse
import mysql.connector 
from django.template import RequestContext
from student.models import *


def sqlError(err):
    response = render_to_response('404.html', {}, context_instance=RequestContext(err))
    response.status_code = 404
    return response

def home(request):
    cursor = connection.cursor()

    books_db = "select distinct b.title, b.barcode, t.DATE from books_db as b, transaction as t where b.barcode = t.barcode and t.cardnumber = '123' group by title;"
    query = "select distinct b.title, b.barcode, t.DATE " + "from books as b, transaction as t" +" where b.barcode = t.barcode and t.cardnumber = '123' group by title union all " + books_db
    
    try:
        cursor.execute(query)
    
    except mysql.connector.Error as err:
        print(err)
        print("Error Code:", err.errno)
        print("SQLSTATE", err.sqlstate)
        print("Message", err.msg)
        return sqlError(err)


    row = cursor.fetchall()   

    if not len(row):
        return HttpResponse("No books issued")

    result = []

    for i in row:

        temp = {}
        temp["title"] = str(i[0])
        temp["barcode"] = str(i[1])
        temp["DATE"] = str(i[2])

        result.append(temp)

    context = {'result' : result}
    cursor.close()
    connection.close()
    return render(request, 'student/issue-history.html', context)

def recommendLibrary(request):
    cursor = connection.cursor()
    query = ""
    libraryResult = []
    title = ""
    searchBook = True 
    blankSearch = True 
    alreadyRecommendedResult = []  
    checkRecommendedBooks = False  # Turns on when user clicks on button to check already recommended books
    newBookRecommendation = False # Turns on when user wants to recommend new book
    newBookRecommended = False
    newTitle = ""
    newAuthor = ""
    newCategory = ""
    hiddenTitle = ""  # Needs to be fixed
    hiddenTitle1 = "" # Needs to be fixed
    newRequest = "False"
    alreadyRequested = "False"
    successMsg = ""
    failMsg = ""
    
    if request.POST.get('title'):
        searchBook = False
        blankSearch = False
        checkRecommendedBooks = False
        newBookRecommendation = False
        newBookRecommended = False

        title = request.POST.get('title')                

        queryBooks = "select barcode, title from bt_map where title like '%" + title + "%' group by title;"

        try:
            cursor.execute(queryBooks)
    
        except mysql.connector.Error as err:
            print(err)
            print("Error Code:", err.errno)
            print("SQLSTATE", err.sqlstate)
            print("Message", err.msg)
            return sqlError(err) 

        row = cursor.fetchall()        
        
        for i in row:

            temp = {}
            temp["barcode"] = str(i[0])
            temp["title"] = str(i[1])
            
            if temp['barcode'].find("DB") > 0:      # barcode contains DB
                queryAuthor = "select author from books_db where barcode = '" + temp['barcode'] + "' ;"
            
            else:
                queryAuthor = "select author from books where barcode = '" + temp['barcode'] + "' ;"
            
            cursor.execute(queryAuthor)
            author = cursor.fetchone()

            if not len(author):
                temp['author'] = "Not Available"
            
            else:
                temp['author'] = str(author[0])

            libraryResult.append(temp)
    
    if request.POST.get('checkRecommendedBooks'):
        searchBook = False
        checkRecommendedBooks = True
        newBookRecommendation = False
        newBookRecommended = False

        hiddenTitle = request.POST.get("hiddenTitle") # hiddenTitle is temp, actually should be title 

        query = "select srNo, bookTitle, author, requestCount from libraryRecommendation where bookTitle like '%" + hiddenTitle + "%' group by bookTitle;"

        print(query)

        cursor.execute(query)
        row = cursor.fetchall()

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

        print(newTitle)
        print(newAuthor)
        print(newCategory)

        #check if same author and title already exists 
        query = "select * from libraryRecommendation where bookTitle = '" + newTitle + "' and author = '" + newAuthor + "';" 
        
        try:
            cursor.execute(query)
    
        except mysql.connector.Error as err:
            print(err)
            print("Error Code:", err.errno)
            print("SQLSTATE", err.sqlstate)
            print("Message", err.msg)
            return sqlError(err) 

        row = cursor.fetchall()

        if not len(row):    # if does not exist insert
            newRequest = True
            recommend = libraryRecommendation.objects.create(bookTitle = newTitle,
                                                         author = newAuthor,
                                                         category = newCategory,
                                                         requestCount = 1)
            recommend.save()

            # Insert into bookRequest also

            getSrNo = "select max(srNo) from libraryRecommendation ;" 
            
            try:
                cursor.execute(getSrNo)                
    
            except mysql.connector.Error as err:
                print("Error in getting serial no from libraryRecommendation")
                print(err)
                print("Error Code:", err.errno)
                print("SQLSTATE", err.sqlstate)
                print("Message", err.msg)
                return sqlError(err)
            
            srNo = cursor.fetchall()

            print(str(srNo[0][0]))
            insertQuery = "insert into bookRequest (srNo, cardnumber) values ('" + str(srNo[0][0]) + "', 'I2K16102102');"

            try :
                cursor.execute(insertQuery)                                
            
            except:         # User has already requested book
                print("Already Voted")
                alreadyRequested = True
                newRequest = False
                failMsg = "You have already requested for this book"
            

            if not failMsg:
                successMsg = "New Book Recommended"

        
        else :  # else update                        

            # Insert vote in bookRequest table cardnumber needed
            insertQuery = "insert into bookRequest (srNo, cardnumber) values ('" + str(row[0][0]) + "', 'I2K16102102');"

            try:
                cursor.execute(insertQuery)
            
            except:         # User has already requested book
                print("Already Voted")
                alreadyRequested = True
                newRequest = False
                failMsg = "You have already requested for this book"

            
            if not alreadyRequested:   #Update requestCount (Has a scope of trigger)
                updateQuery = "update libraryRecommendation set requestCount = requestCount + 1 where bookTitle = '" + newTitle + "' and author = '" + newAuthor + "';" 
                try:
                    cursor.execute(updateQuery)
        
                except mysql.connector.Error as err:
                    print(err)
                    print("Error Code:", err.errno)
                    print("SQLSTATE", err.sqlstate)
                    print("Message", err.msg)
                    return sqlError(err)
            
            if not failMsg:
                successMsg = "New Book Recommended"
            
            

    if request.POST.get("increaseRequestCount"):        

        alreadyRequested = False
        newRequest = True
        newBookRecommended = True

        srNo = request.POST.get("increaseRequestCount")
        insertQuery = "insert into bookRequest (srNo, cardnumber) values ('" + srNo + "', 'I2K16102102');"
        
        try:
            cursor.execute(insertQuery)
        
        except:         # User has already requested book
            print("Already Voted")
            alreadyRequested = True
            newRequest = False
            failMsg = "You have already requested for this book"

        
        if not alreadyRequested:   #Update requestCount (Has a scope of trigger)            
            updateQuery = "update libraryRecommendation set requestCount = requestCount + 1 where srNo = '" + srNo + "';" 
            try:
                cursor.execute(updateQuery)
                print(updateQuery)
    
            except mysql.connector.Error as err:
                print(err)
                print("Error Code:", err.errno)
                print("SQLSTATE", err.sqlstate)
                print("Message", err.msg)
                return sqlError(err)
        
        if not failMsg:
                successMsg = "New Book Recommended"
        

    context = {
        'searchBook' : searchBook,
        'libraryResult' : libraryResult,
        'blankSearch' : blankSearch,
        'alreadyRecommendedResult' : alreadyRecommendedResult,
        'checkRecommendedBooks' : checkRecommendedBooks,
        'newBookRecommendation' : newBookRecommendation,
        'newTitle' : newTitle,
        'newAuthor' : newAuthor,
        'newCategory' : newCategory,
        'newBookRecommended' : newBookRecommended,
        'title' : title,
        'alreadyRequested' : alreadyRequested,
        'newRequest' : newRequest,
        'failMsg' : failMsg,
        'successMsg' : successMsg,
        'hiddenTitle' : hiddenTitle,     # Needs to be fixed
        'hiddenTitle1' : hiddenTitle1
        }
        
    cursor.close()
    connection.close()
    return render(request, 'student/recommend-library.html', context)
