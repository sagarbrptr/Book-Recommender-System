# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import connection, transaction
from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import RequestContext
import random
import json
from django.contrib.admin.views.decorators import staff_member_required

from django.core.cache import cache
from django.views.decorators.cache import cache_page
from ml.views import ML


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


def incrementNewTransaction(database):

    selectQuery = "select * from newTransactions"
    errorMsg = "Error in selecting from newTransactions"

    newTransactionCount = database.select(selectQuery, errorMsg)

    # If select is successful
    if newTransactionCount:
        count = newTransactionCount[0][0]
        print(count)

        # if count == 49:
            # print("Generating CSV wait")
            # ml = ML()
            # ml.createCSV(database)
            # print("CSV created successfully")
        
        print("Generating CSV wait")
        ml = ML()
        ml.createCSV(database)
        print("CSV created successfully")

        count = (count + 1) % 50

        # Update newTransaction
        updateQuery = "update newTransactions set Count = '" + \
            str(count) + "';"
        errorMsg = "Error in updating entry of newTransactions"

        # If update successful, success
        if database.insertOrUpdateOrDelete(updateQuery, errorMsg):
            return True

        # Else, update unsuccessful, error
        else:
            return False
    # Else, error in read, error
    else:
        return False


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
            # select max bookSrNo from bt_map
            selectQuery = "select max(bookSrNo) from bt_map"
            errorMsg = "error in selecting max of bookSrNo from bt_map"

            maxBookSrNo = database.select(selectQuery, errorMsg)

            # If valid maxBookSrNo increment
            if maxBookSrNo:
                newSrNo = maxBookSrNo[0][0] + 1

                # insert in bt_map
                insertQuery = "insert into bt_map values ('" + \
                    newBarocde + "', '" + newTitle + \
                    "', '" + str(newSrNo) + "');"
                errorMsg = "Error in insertion in bt_map"

                # If insertion is successful
                if database.insertOrUpdateOrDelete(insertQuery, errorMsg):
                    database.commit()
                    return True

                # Else, error in insertion of bt_map, rollback
                else:
                    database.rollback()
                    return False
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

        # Check if given barcode exists or not
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
    RequestedBookSrNo = ""
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

        # Insert in books
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
        'RequestedBookSrNo': RequestedBookSrNo,
        'deleteSuccessful': deleteSuccessful,
        'operationSuccessful': operationSuccessful,
        'failReason': failReason
    }

    return render(request, 'librarian/librarian-recommendation.html', context)


@staff_member_required
@cache_page(60 * 15)
def librarianStatistics(request):
    mostIssuedBooks = []
    mostRequestedBooks = []
    highestRatedBooks = []
    mostFrequentReader = []
    database = DB()

    # Most Issued Books
    query = "select books.title as title, count(books.title) as count " + \
        "from books, transaction where transaction.barcode = books.barcode " + \
            "group by title order by count(books.title) desc limit 10;"
    errorMsg = "Error in selecting Most Issued Books"

    row = database.select(query, errorMsg)
    if row:
        for i in row:
            temp = {}
            temp['title'] = i[0]
            temp['issueCount'] = i[1]

            mostIssuedBooks.append(temp)

    # Most Requested Books
    query = "select * from libraryRecommendation " + \
        "where requestCount != 1 order by requestCount desc limit 10;"
    errorMsg = "Error in selecting Most Requested Books"

    row = database.select(query, errorMsg)
    if row:
        for i in row:
            temp = {}
            temp['title'] = i[1]
            temp['author'] = i[2]
            temp['requestCount'] = i[4]

            mostRequestedBooks.append(temp)

    # Highest Rated book according to rating and isuue count
    query = "select barcode, rating, count(barcode) " + \
        "from ratings group by barcode order by rating desc, count(barcode) desc limit 10;"
    errorMsg = "Error in selecting Highest Rated Books"

    row = database.select(query, errorMsg)
    if row:
        for i in row:
            temp = {}
            temp['barcode'] = row[0]
            temp['rating'] = row[1]
            temp['issueCount'] = row[2]

            # Select Book name
            selectBook = "select title from books where barcode = '" + \
                str(i[0]) + "';"
            errorMsg = "Error in selecting book name"

            bookName = database.select(selectBook, errorMsg)
            if bookName:
                temp['title'] = bookName[0][0]
            else:
                temp['title'] = "Not Available"

            highestRatedBooks.append(temp)

    # Most Frequent Reader
    query = "select cardnumber, count(cardnumber) as count " + \
        "from transaction group by cardnumber order by count(cardnumber) desc limit 10;"
    errorMsg = "Error in selecting Most Frequent Reader"

    row = database.select(query, errorMsg)
    if row:
        for i in row:
            temp = {}
            temp['cardnumber'] = i[0]
            temp['issueCount'] = i[1]

            # Select User name from user table
            selectUser = "select Name from user where cardnumber = '" + \
                str(i[0]) + " ';"
            errorMsg = "Error in selecting user"

            user = database.select(selectUser, errorMsg)
            if user:
                temp['name'] = user[0][0]
            else:
                temp['name'] = "Not Available"

            mostFrequentReader.append(temp)

    # python dictionaries converted to json objects
    context = {
        'mostIssuedBooks': json.dumps(mostIssuedBooks),
        'mostRequestedBooks': json.dumps(mostRequestedBooks),
        'highestRatedBooks': json.dumps(highestRatedBooks),
        'mostFrequentReader': json.dumps(mostFrequentReader),
    }

    return render(request, 'librarian/librarian-statistics.html', context)


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
            if validTitle:
                # Needed in getting barcode from bt_map
                title = validTitle[0][0]
                insertTransactionQuery = "insert into transaction VALUES (default, CURDATE(), '" + newBarocde + "', '" + newCardNumber + \
                    "', (select name from user where cardnumber = '" + \
                    newCardNumber + "'), '" + newBranchCode + "');"
                errMsg = "Error in inserting in transaction"
                # print(insertTransactionQuery)

                # If insert in transaction successful,
                # insert in ratings through ratings
                if database.insertOrUpdateOrDelete(insertTransactionQuery, errMsg):
                    # Get Barcode and bookSrNo from bt_map
                    selectBarcodeBt_map = "select barcode, bookSrNo from bt_map where title = '" + title + "';"
                    errorMsg = "Error in selecting barcode from bt_map"

                    validBarcode = database.select(
                        selectBarcodeBt_map, errorMsg)

                    # If valid barcode,
                    # check if same barcode and same user already exists in ratings

                    if validBarcode:
                        barcode = validBarcode[0][0]
                        bookSrNo = validBarcode[0][1]

                        selectRating = "select * from ratings where barcode = '" + \
                            barcode + "' and cardnumber = '" + newCardNumber + "';"
                        errorMsg = "Error in selecting from ratings"

                        # If no entry in ratings
                        # insert in ratings
                        if not database.select(selectRating, errorMsg):
                            insertRatingsQuery = "insert into ratings values ('" + newCardNumber + "', '" + barcode + "', '" + str(
                                random.randrange(1, 6)) + "', '0', (select SrNo from user where cardnumber = '" + newCardNumber + "'), '" + \
                                str(bookSrNo) + "');"
                            errorMsg = "Error in inserting in ratings"

                            # If insert successful, increment
                            if database.insertOrUpdateOrDelete(insertRatingsQuery, errorMsg):

                                # If increment successful, commit
                                if incrementNewTransaction(database):
                                    issueSuccessful = True
                                    database.commit()

                                # Else error in increment count of new Transaction, rollback
                                else:
                                    database.rollback()

                            # Else, error in inserting in ratings, commit
                            else:
                                ErrMsg = "Error in inserting in ratings"
                                database.rollback()

                        # Else, a rating already exists for given set,
                        # increment count of new Transaction
                        else:

                            # If increment successful, commit
                            if incrementNewTransaction(database):
                                issueSuccessful = True
                                database.commit()

                            # Else error in increment count of new Transaction, rollback
                            else:
                                database.rollback()

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
