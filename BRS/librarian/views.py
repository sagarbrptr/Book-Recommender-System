# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import connection, transaction
from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import RequestContext
import random
from django.contrib.admin.views.decorators import staff_member_required

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


def insertBook(request, database):

    # Start transaction
    database.beginTransaction()

    newBarocde = str(request.POST.get("newBarocde"))
    newTitle = request.POST.get("newTitle")
    newAuthor = request.POST.get("newAuthor")
    newSubject = request.POST.get("newSubject")

    submitQuery = "Insert into books values('" + newBarocde + "', curdate(), '" + \
        newTitle + "', '" + newAuthor + "', '" + newSubject + "');"
    print(submitQuery)

    errorMsg = "Error in inserting in books"
    # print(submitQuery)

    # If insert successful,
    # check in bt_map if same title exists
    if database.insertOrUpdateOrDelete(submitQuery, errorMsg):

        selectQuery = "select * from bt_map where title = '" + newTitle + "';"
        errorMsg = "Error in selecting from bt_map"

        # If there exists an entry with same name, commit
        if database.select(selectQuery, errorMsg):
            database.commit()
            return True

        # Else, enter in bt_map
        else:
            insertQuery = "insert into bt_map values ('" + \
                newBarocde + "', '" + newTitle + "');"
            errorMsg = "Error in insertion in bt_map"

            # If insertion is successful, commit
            if database.insertOrUpdateOrDelete(insertQuery, errorMsg):
                database.commit()
                return True

            # Else, error in insertion of bt_map, rollback
            else:
                database.rollback()
                return False

        # Else error in inserting in books
    else:
        database.rollback()
        return False

@staff_member_required
def librarianHome(request):

    insertSuccessful = False
    insertFormSubmitted = False
    deleteFormSubmitted = False
    deleteSuccessful = False
    deletionErrorMsg = "Error in deleting book"
    insertionErrorMsg = "Error in inserting book"

    if request.POST.get("newBookSubmit"):       # Insert books
        database = DB()
        insertFormSubmitted = True

        # Insert in books
        insertSuccessful = insertBook(request, database)

    if request.POST.get("deleteBookSubmit"):        # Delete Books
        database = DB()

        deleteFormSubmitted = True
        deleteBarcode = str(request.POST.get("deleteBarcode"))

        # Start Transaction
        database.beginTransaction()

        table = "books"

        selectQuery = "select * from " + table + \
            " where barcode = '" + deleteBarcode + "';"
        errorMsg = "Error in selecting from " + table
        # print(selectQuery)

        # If there exists row, insert in deletedBooks
        if database.select(selectQuery, errorMsg):
            insertQuery = "insert into deletedBooks select * from " + table + " where barcode = '" + \
                deleteBarcode + "';"
            errorMsg = "Error in inserting in deletedBooks"
            # print(insertQuery)

            # If Successful insertion, delete from books
            if database.insertOrUpdateOrDelete(insertQuery, errorMsg):
                deleteQuery = "delete from " + table + \
                    " where barcode = '" + deleteBarcode + "';"
                errorMsg = "Error in deleting from  " + table
                # print(deleteQuery)

                if database.insertOrUpdateOrDelete(deleteQuery, errorMsg):
                    deleteSuccessful = True
                    database.commit()

                else:   # Else, error in deletion,  rollback
                    deletionErrorMsg = "Error in deleting from " + table
                    database.rollback()

            # Else, Error in insertion, Rollback
            else:
                print("Error")
                deletionErrorMsg = "Error in inserting in deletedBooks"
                database.rollback()

        else:   # Else book does not exists, Rollback
            database.commit()
            deletionErrorMsg = "Book with given barcode does not exists or is already deleted"

    context = {
        "insertSuccessful": insertSuccessful,
        "insertFormSubmitted": insertFormSubmitted,
        "deleteFormSubmitted": deleteFormSubmitted,
        "deleteSuccessful": deleteSuccessful,
        "deletionErrorMsg": deletionErrorMsg,
        "insertionErrorMsg": insertionErrorMsg,
    }

    return render(request, 'librarian/librarian-home.html', context)

@staff_member_required
def librarianRecommendation(request):
    recommendedBook = []
    insertSuccessful = False
    addRequestedBookFormSubmitted = False
    deleteSuccessful = False
    failReason = "Error in inserting books"
    operationSuccessful = False
    database = DB()

    selectQuery = "select * from libraryRecommendation order by requestCount desc, srNo;"
    errorMsg = "Error in getting data from libraryRecommendation"

    row = database.select(selectQuery, errorMsg)
    # Handle null row exception directly in html using len
    if row:
        for i in row:
            temp = {}
            # had to use str() because when passing object to
            temp["srNo"] = str(i[0])
            temp["title"] = str(i[1])  # insertRequestedBook, indexes get u''.
            temp["author"] = str(i[2])
            temp["subject"] = str(i[3])
            temp["requestCount"] = str(i[4])
            # print(temp["requestCount"])
            recommendedBook.append(temp)

    if request.POST.get("addRequestedBook"):    # Add a recommended book to library
        addRequestedBookFormSubmitted = True

        RequestedBookSrNo = request.POST.get("RequestedBookSrNo")
        # print(RequestedBookSrNo)

        # Start transaction
        database.beginTransaction()

        # Insert in books or books_db
        # Insertion Successful, delete from libraryRecommendation
        if insertBook(request, database):

            deleteQuery = "delete from libraryRecommendation where srNo = '" + \
                RequestedBookSrNo + "';"
            errorMsg = "Error in deleting from libraryRecommendation"
            # print(deleteQuery)

            # Deletion successful, commit
            if database.insertOrUpdateOrDelete(deleteQuery, errorMsg):
                deleteSuccessful = True
                operationSuccessful = True
                database.commit()

            else:  # Else, deletion failed, rollback
                failReason = "Error in deletion from libraryRecommendation"
                deleteSuccessful = False
                database.rollback()

        else:  # Else, insert failed, rollback
            failReason = "Error in insertion in books table"
            database.rollback()

    context = {
        'recommendedBook': recommendedBook,
        'addRequestedBookFormSubmitted': addRequestedBookFormSubmitted,
        'insertSuccessful': insertSuccessful,
        'deleteSuccessful': deleteSuccessful,
        'operationSuccessful': operationSuccessful,
        'failReason': failReason
    }

    return render(request, 'librarian/librarian-recommendation.html', context)

@staff_member_required
def librarianStatistics(request):
    return render(request, 'librarian/librarian-statistics.html')

@staff_member_required
def issueBook(request):
    database = DB()
    issueFormSubmitted = False
    issueSuccessful = False
    ErrMsg = "Error in Issuing book"

    if request.POST.get("newIssueSubmit"):
        issueFormSubmitted = True

        newBarocde = str(request.POST.get("newBarocde"))
        newCardNumber = request.POST.get("newCardNumber")
        newBranchCode = request.POST.get("newBranchCode")

        # Start Transaction
        database.beginTransaction()

        selectUser = "select cardnumber, Name from user where cardnumber = '" + \
            newCardNumber + "';"
        errorMsg = "Error in selcting from user"        

        # If a valid user, check barcode
        if database.select(selectUser, errorMsg):           
            table = "books"

            selectBarcode = "select title from " + table + " where barcode = '" + \
                newBarocde + "';"
            errorMsg = "Error in selecting from books"
            
            validTitle = database.select(selectBarcode, errorMsg)
            # If a valid barcode, insert in transaction
            if validTitle : 
                title = validTitle[0][0] # Needed in getting barcode from bt_map
                insertTransactionQuery = "insert into transaction VALUES (default, CURDATE(), '" + newBarocde + "', '" + newCardNumber + \
                    "', (select name from user where cardnumber = '" + \
                    newCardNumber + "'), '" + newBranchCode + "');"
                errMsg = "Error in inserting in transaction"
                # print(insertTransactionQuery)

                # If insert in transaction successful, 
                # insert in ratings through ratings
                if database.insertOrUpdateOrDelete(insertTransactionQuery, errMsg):                    
                    # Get Barcode from bt_map
                    selectBarcodeBt_map = "select barcode from bt_map where title = '" + title + "';"
                    errorMsg = "Error in selecting barcode from bt_map"

                    validBarcode = database.select(selectBarcodeBt_map, errorMsg)

                    # If valid barcode, 
                    # check if same barcode and same user already exists in ratings                                        
                    
                    if validBarcode:
                        barcode = validBarcode[0][0]

                        selectRating = "select * from ratings where barcode = '" + barcode + "' and cardnumber = '" + newCardNumber + "';"
                        errorMsg = "Error in selecting from ratings"

                        # If no entry in ratings 
                        # insert in ratings
                        if not database.select(selectRating, errorMsg):                      
                            insertRatingsQuery = "insert into ratings values ('" + newCardNumber + "', '" + barcode + "', '" + str(random.randrange(1, 6)) + "', '0');"
                            errorMsg = "Error in inserting in ratings"

                            #If insert successful, commit
                            if database.insertOrUpdateOrDelete(insertRatingsQuery, errorMsg):
                                issueSuccessful = True
                                database.commit()
                            
                            # Else, error in inserting in ratings, commit
                            else:
                                ErrMsg = "Error in inserting in ratings"
                                database.rollback()
                        
                        # Else, a rating already exists for given set, commit
                        else:
                            issueSuccessful = True
                            database.commit()

                    # Else, error in getting barcode from bt_map, rollback
                    else:
                        ErrMsg = "Error in getting barcode from bt_map"
                        database.rollback()

                # Else, error in inserting in transaction, rollback                                            
                else:
                    ErrMsg = "Error in inserting in transaction table"
                    database.rollback()

            # Else, invalid barcode, rollback
            else:
                ErrMsg = "Invalid barcode"
                database.rollback()

        # Else, invalid user, rollback
        else:
            ErrMsg = "Invalid user"
            database.rollback()

    context = {
        'issueFormSubmitted': issueFormSubmitted,
        'issueSuccessful': issueSuccessful,
        'ErrMsg': ErrMsg,
    }

    return render(request, 'librarian/issue-book.html', context)
