# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class ratings(models.Model):
    cardnumber = models.CharField(max_length = 14, primary_key = True)
    barcode = models.CharField(max_length = 9)
    rating = models.IntegerField()
    valid = models.IntegerField(default = 0)
    userSrNo = models.IntegerField()

    class Meta:
        db_table = 'ratings'
        managed = False
        unique_together = (('cardnumber', 'barcode'),)


class books(models.Model):
    barcode = models.CharField(max_length = 10, primary_key = True)
    dateaccessioned = models.DateField()
    title = models.CharField(max_length = 100)
    author = models.CharField(max_length = 45)
    Subject = models.CharField(max_length = 35)

    class Meta:
        db_table = 'books'
        managed = False

class bt_map(models.Model):
    barcode = models.CharField(max_length = 200, primary_key = True)
    title = models.CharField(max_length = 200)

    class Meta:
        db_table = 'bt_map'
        managed = False


class user(models.Model):
    SrNo = models.IntegerField()
    cardnumber = models.CharField(max_length = 14, primary_key = True)
    Roll_No = models.IntegerField()
    Name = models.CharField(max_length = 35)
    Gender = models.CharField(max_length = 6)
    Class = models.CharField(max_length = 28)
    Student_EMail = models.CharField(max_length = 37)

    class Meta:
        db_table = 'user'
        managed = False

class transaction(models.Model):
    transaction_id = models.AutoField(primary_key = True)
    DATE = models.DateField()
    barcode = models.ForeignKey(books,on_delete=models.CASCADE)
    cardnumber = models.ForeignKey(user,on_delete=models.CASCADE)
    Name = models.CharField(max_length = 39)
    branchcode = models.CharField(max_length = 4)

    class Meta:
        db_table = 'transaction'
        managed = False

class libraryRecommendation(models.Model):
    srNo = models.AutoField(primary_key = True)
    bookTitle = models.CharField(max_length = 250)
    author= models.CharField(max_length = 250)
    category= models.CharField(max_length = 250)
    requestCount= models.IntegerField()

    class Meta:
        db_table = 'libraryRecommendation'
        managed = False

class bookRequest(models.Model):
    srNo = models.AutoField(primary_key = True)
    cardnumber = models.CharField(max_length = 14)
    requestCount = models.IntegerField(default = 1)

    class Meta:
        db_table = 'bookRequest'
        managed = False
        unique_together = (('srNo', 'cardnumber'),)

class deletedBooks(models.Model):
    barcode = models.CharField(max_length = 8, primary_key = True)
    dateaccessioned = models.DateField()
    title = models.CharField(max_length = 105)
    author = models.CharField(max_length = 43)
    Subject = models.CharField(max_length = 35)

    class Meta:
        db_table = 'deletedBooks'
        managed = False
