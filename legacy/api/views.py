from rest_framework import views, viewsets, generics
from rest_framework.response import Response

from .serializers import *
import requests


GOOGLE_API_KEY = 'AIzaSyBDOWG9r9e517jsLCZcKgp09RYvvqXNMgA='


class getGoogleHeight(viewsets.ViewSet):
    '''
        Usage: /api/get-google-elevation/?lat=55.74777381&lon=37.595482797
        Output: {"elevation": "139.9174194335938"}
        -----------------------
        Usage original: https://maps.googleapis.com/maps/api/elevation/json?locations=37.395744,55.644466&key=GOOGLE_API_KEY
        Output original: 
        {
            "results" : [
                {
                    "elevation" : 182.48095703125,
                    "location" : {
                        "lat" : 55.644466,
                        "lng" : 37.395744
                    },
                    "resolution" : 19.08790397644043
                }
            ],
            "status" : "OK"
        }
    '''
    serializer_class = googleHeigthSerializer

    def list(self, request, format=None):
        lat = self.request.query_params.get('lat', None)
        lon = self.request.query_params.get('lon', None)
        results = None
        data = {}
        if lat and lon:
            # если я снова не путаю X с Y
            URL = f'https://maps.googleapis.com/maps/api/elevation/json?locations={lat},{lon}&key={GOOGLE_API_KEY}'
            response = requests.get(URL)
            if not response.raise_for_status():
                if data.get('elevation'):
                    data['elevation'] = response.json()['results'][0]['elevation']
                    results = googleHeigthSerializer(data).data
        return Response(results)