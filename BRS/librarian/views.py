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
        


def insertInBooks(request):
    newBarocde = request.POST.get("newBarocde")
    newTitle = request.POST.get("newTitle")
    newAuthor = request.POST.get("newAuthor")
    newSubject = request.POST.get("newSubject")

    database = DB()    

    submitQuery = "Insert into books values('" + newBarocde + "', curdate(), '" + newTitle + "', '" + newAuthor + "', '" + newSubject + "');"
    errorMsg = "Error in inserting in books"
    print(submitQuery)        

    return database.insertOrUpdateOrDelete(submitQuery, errorMsg)
    

def librarianHome(request):

    insertSuccessful = False
    insertFormSubmitted = False
    deleteFormSubmitted = False
    deleteSuccessful = False
    deletionErrorMsg = "Error in deleting book"

    if request.POST.get("newBookSubmit"):  
        insertFormSubmitted = True           
        insertSuccessful = insertInBooks(request)
    
    if request.POST.get("deleteBookSubmit"):
        deleteFormSubmitted = True
        deleteBarocde = request.POST.get("deleteBarocde")

        database = DB()

        selectQuery = "select * from books where barcode = '" + deleteBarocde + "';"
        errorMsg = "Error in selecting from books"
        print(selectQuery)

        if database.select(selectQuery, errorMsg):  # If there exists row, insert in deletedBooks
            insertQuery = "insert into deletedBooks select * from books where barcode = '" + deleteBarocde + "';"
            errorMsg = "Error in inserting in deletedBooks"
            print(insertQuery)

            if database.insertOrUpdateOrDelete(insertQuery, errorMsg):  #If Successful delete from books
                deleteQuery = "delete from books where barcode = '" + deleteBarocde + "';"
                errorMsg = "Error in deleting from Books"
                print(deleteQuery)

                deleteSuccessful = database.insertOrUpdateOrDelete(deleteQuery, errorMsg)                        
        
        else:   # Else book does not exists
            deletionErrorMsg = "Book with given barcode does not exists or is already deleted"
    
    context = {
        "insertSuccessful" : insertSuccessful,
        "insertFormSubmitted" : insertFormSubmitted,
        "deleteFormSubmitted" : deleteFormSubmitted,
        "deleteSuccessful" : deleteSuccessful,
        "deletionErrorMsg" : deletionErrorMsg,
    }

    return render(request,'librarian/librarian-home.html', context)

def librarianRecommendation(request):
    recommendedBook = []   
    insertSuccessful = False  
    addRequestedBookFormSubmitted = False
    deleteSuccessful = False
    database = DB()

    selectQuery = "select * from libraryRecommendation order by requestCount desc, srNo;"
    errorMsg = "Error in getting data from libraryRecommendation"

    row = database.select(selectQuery, errorMsg)
    # Handle null row exception directly in html using len
    for i in row:
        temp = {}
        temp[str("srNo")] = str(i[0])   # had to use str() because when passing object to
        temp[str("title")] = str(i[1])  # insertRequestedBook, indexes get u''.
        temp[str("author")] = str(i[2])
        temp[str("subject")] = str(i[3])
        temp[str("requestCount")] = str(i[4])        
        # print(temp["requestCount"])
        recommendedBook.append(temp)
    
    if request.POST.get("addRequestedBook"):        
        addRequestedBookFormSubmitted = True

        RequestedBookSrNo = request.POST.get("RequestedBookSrNo")
        #print(RequestedBookSrNo)
        insertSuccessful = insertInBooks(request)

        if insertSuccessful:
            db = DB()

            deleteQuery = "delete from libraryRecommendation where srNo = '" + RequestedBookSrNo + "';"
            errorMsg = "Error in deleting from libraryRecommendation"
            print(deleteQuery)
            deleteSuccessful = db.insertOrUpdateOrDelete(deleteQuery, errorMsg)


    context = {
        'recommendedBook' : recommendedBook,
        'addRequestedBookFormSubmitted' : addRequestedBookFormSubmitted, 
        'insertSuccessful' : insertSuccessful,
        'deleteSuccessful' : deleteSuccessful   
    }

    return render(request,'librarian/librarian-recommendation.html', context)

def librarianStatistics(request):
    return render(request,'librarian/librarian-statistics.html')
