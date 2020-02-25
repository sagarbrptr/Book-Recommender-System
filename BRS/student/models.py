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
