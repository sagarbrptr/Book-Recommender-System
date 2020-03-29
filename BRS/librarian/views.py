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
        


    

def librarianHome(request):

    insertSuccessful = False
    insertFormSubmitted = False
    deleteFormSubmitted = False
    deleteSuccessful = False
    deletionErrorMsg = "Error in deleting book"

    if request.POST.get("newBookSubmit"):
        newBarocde = request.POST.get("newBarocde")
        newTitle = request.POST.get("newTitle")
        newAuthor = request.POST.get("newAuthor")
        newSubject = request.POST.get("newSubject")

        database = DB()
        insertFormSubmitted = True

        submitQuery = "Insert into books values('" + newBarocde + "', curdate(), '" + newTitle + "', '" + newAuthor + "', '" + newSubject + "');"
        errorMsg = "Error in inserting in books"
        #print(submitQuery)        

        insertSuccessful = database.insertOrUpdateOrDelete(submitQuery, errorMsg)
    
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
    database = DB()

    selectQuery = "select * from libraryRecommendation order by requestCount desc, srNo;"
    errorMsg = "Error in getting data from libraryRecommendation"

    row = database.select(selectQuery, errorMsg)
    # Handle null row exception directly in html using len
    for i in row:
        temp = {}
        temp["title"] = str(i[1])
        temp["author"] = str(i[2])
        temp["requestCount"] = str(i[4])        
        print(temp["requestCount"])
        recommendedBook.append(temp)

    context = {
        'recommendedBook' : recommendedBook,
    }

    return render(request,'librarian/librarian-recommendation.html', context)

def librarianStatistics(request):
    return render(request,'librarian/librarian-statistics.html')
