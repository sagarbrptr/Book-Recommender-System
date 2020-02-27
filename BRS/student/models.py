# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class ratings(models.Model):
    cardnumber = models.CharField(max_length = 14, primary_key = True)
    barcode = models.CharField(max_length = 9)
    rating = models.IntegerField()

    class Meta:
        db_table = 'ratings'
        managed = False
        unique_together = (('cardnumber', 'barcode'),)
<<<<<<< HEAD
=======

class books(models.Model):
    barcode = models.CharField(max_length = 8, primary_key = True)
    dateaccessioned = models.DateField()
    title = models.CharField(max_length = 105)
    author = models.CharField(max_length = 43)
    Subject = models.CharField(max_length = 35)

    class Meta:
        db_table = 'books'
        managed = False

class books_db(models.Model):
    barcode = models.CharField(max_length = 9, primary_key = True)
    dateaccessioned = models.DateField()
    title = models.CharField(max_length = 100)
    author = models.CharField(max_length = 37)
    Subject = models.CharField(max_length = 15)

    class Meta:
        db_table = 'books_db'
        managed = False

class bt_map(models.Model):
    barcode = models.CharField(max_length = 200, primary_key = True)
    title = models.CharField(max_length = 200)

    class Meta:
        db_table = 'bt_map'
        managed = False


class user(models.Model):
    SrNo = models.IntegerField()
    barcode_no = models.CharField(max_length = 11, primary_key = True)
    Roll_No = models.IntegerField()
    Name = models.CharField(max_length = 35)
    Gender = models.CharField(max_length = 6)
    Class = models.CharField(max_length = 28)
    Student_EMail = models.CharField(max_length = 37)

    class Meta:
        db_table = 'user'
        managed = False

class transaction(models.Model):
    transaction_id = models.IntegerField(primary_key = True)
    DATE = models.DateField()
    barcode = models.CharField(max_length = 9)
    cardnumber = models.CharField(max_length = 14)
    Name = models.CharField(max_length = 39)
    branchcode = models.CharField(max_length = 4)

    class Meta:
        db_table = 'transaction'
        managed = False
>>>>>>> d5005020b3c1a1080daf22e54345e35d53981adf
