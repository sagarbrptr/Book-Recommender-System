# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from .apps import MlConfig

from django.http import JsonResponse
from rest_framework.views import APIView
class call_model(APIView):
    def get(self,request):
        if request.method == 'GET':
            # get sound from request
            sound = request.GET.get('sound')
   
            # vectorize sound
            vector = MlConfig.vectorizer.transform([sound])
            # predict based on vector
            prediction = MlConfig.regressor.predict(vector)[0]
            # build response
            response = {'dog': prediction}
            # return response
            return JsonResponse(response)