# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import connection, transaction
from django.shortcuts import render
from django.http import HttpResponse 

def home(request):
    cursor = connection.cursor()

    books_db = "select distinct b.title, b.barcode, t.DATE from books_db as b, transaction as t where b.barcode = t.barcode and t.cardnumber = 'I2K16102142' group by title;"

    cursor.execute("select distinct b.title, b.barcode, t.DATE " + 
                    "from books as b, transaction as t" +
                    " where b.barcode = t.barcode and t.cardnumber = '123' group by title union all " + books_db)
    row = cursor.fetchall()

    # print(row)

    result = []

    for i in row:

        print(i[0])
        print(i[1])

        temp = {}
        temp["title"] = str(i[0])
        temp["barcode"] = str(i[1])
        temp["DATE"] = str(i[2])

        result.append(temp)

    context = {'result' : result}
    return render(request, 'student/tables.html', context)

    # return HttpResponse(result)