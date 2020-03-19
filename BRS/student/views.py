# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import connection, transaction
from django.shortcuts import render, render_to_response
from django.http import HttpResponse
import mysql.connector 
from django.template import RequestContext
from student.models import libraryRecommendation


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
    return render(request, 'student/tables.html', context)

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
    
    if request.POST.get('title'):
        searchBook = False
        blankSearch = False
        checkRecommendedBooks = False
        newBookRecommendation = False
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
        query = "select srNo, bookTitle, author from libraryRecommendation where bookTitle like '%" + title + "%' group by bookTitle;"
        
        cursor.execute(query)
        row = cursor.fetchall()

        for i in row:

            temp = {}  
            temp["srNo"] = str(i[0])          
            temp["title"] = str(i[1])
            temp["author"] = str(i[2])

            alreadyRecommendedResult.append(temp)
    
    if request.POST.get('newBookRecommendation'):
        newBookRecommendation = True
        searchBook = False
        checkRecommendedBooks = False
    
    if request.POST.get('newBookSubmit'):
        newBookRecommendation = True
        searchBook = False
        checkRecommendedBooks = False

        newTitle = request.POST.get('newTitle')
        newAuthor = request.POST.get('newAuthor')
        newCategory = request.POST.get('newCategory')


        # query = "insert into libraryRecommendation values (default, '" + newTitle + "', '" + newAuthor + "', '" + newCategory + "', 1);"
        # commit = "commit;"

        # cursor.execute(query)
        # cursor.execute(commit)
        # connection.commit()

        recommend = libraryRecommendation()
        recommend.bookTitle = newTitle        
        recommend.author = newAuthor
        recommend.category = newCategory
        recommend.requestCount = 1

    context = {
        'searchBook' : searchBook,
        'libraryResult' : libraryResult,
        'blankSearch' : blankSearch,
        'alreadyRecommendedResult' : alreadyRecommendedResult,
        'checkRecommendedBooks' : checkRecommendedBooks,
        'newBookRecommendation' : newBookRecommendation
        }
        
    cursor.close()
    connection.close()
    return render(request, 'student/recommend-library.html', context)
