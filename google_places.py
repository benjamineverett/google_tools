# @Author: Benjamin R. Everett <beneverett>
# @Date:   01-22-2018
# @Email:  benjamin.r.everett@gmail.com
# @Filename: google_places.py
# @Last modified by:   beneverett
# @Last modified time: 01-22-2018

import requests
import os
import json


class GooglePlaces(object):

    def __init__(self,
                 api_key=None,
                 internal_api_key=None):

        self.api_key = api_key
        self._initialize(internal_api_key)
        self.requested_info = None

    def _initialize(self, internal_api_key):
        if self.api_key is None:
            self.api_key = os.environ.get(internal_api_key)

    def fetch_metadata_info(self, address):
        self.meta_data_response = self._hit_api(api='meta_data',
                                                address=address)

    def fetch_radius_info(self, address, radius=5):
        lat_lng = self._get_lat_lng(address=address)
        self.radius_response = self._hit_api(api='radius',
                                             location=lat_lng,
                                             radius=radius)

    def fetch_detailed_info(self, address=None, place_id=None):
        if address:
            response = self.fetch_radius_info(address=address)
            # take the number e.g. for '2801 ash st' we want '2801'
            address.split(' ')[0]

    def fetch_text_info(self, address):
        self.text_response = self._hit_api(api='text', address=address)

        pass

    def _get_lat_lng(self, address):
        response = self._hit_api(api='meta_data',
                                 address=address)
        lat = response.json()['location']['lat']
        lng = response.json()['location']['lng']

        return lat, lng

    def _hit_api(self,
                 api,
                 place_id=None,
                 lat_lng=None,
                 radius=None,
                 address=None):
        link = self._api(api)
        payload = self._payload_settings(api,
                                         place_id,
                                         lat_lng,
                                         radius,
                                         address)

        return requests.get(link, params=payload)

    def _api(self, api):
        place_api = {
            "details":
            "https://maps.googleapis.com/maps/api/place/details/json?",
            "radius":
            "https://maps.googleapis.com/maps/api/place/nearbysearch/json?",
            "text":
            "https://maps.googleapis.com/maps/api/place/textsearch/json?",
            "meta_data":
            "https://maps.googleapis.com/maps/api/streetview/metadata?"
                     }
        return place_api[api]

    def _payload_settings(self,
                          payload_name,
                          place_id=None,
                          lat_lng=None,
                          radius=None,
                          address=None):

        api_key = self.api_key
        if self.api_key is None:
            api_key = os.environ.get(internal_api_key)

        payloads = {
            "details":
                {"place_id": place_id,
                 "key": api_key},
            "radius":
                {"location": "{},{}".format(lat_lng[0], lat_lng[1]),
                 "radius": radius,
                 "key": api_key},
            "text":
                {"query": address,
                 "key": api_key},
            "meta_data":
                {"location": address,
                 "key": api_key},
            }

        return payloads[payload_name]

    def _get_details(self, address):
        details_link = \
            "https://maps.googleapis.com/maps/api/place/details/json?"

        num = address.split(' ')[0]

        self.businesses_ids = \
            [self.info_radius.json()['results'][i]['place_id']
             for i in range(len(self.info_radius.json()['results']))]
             # if self.info_radius.json()
             # ['results'][i]['vicinity'].split(' ')[0] == num]

        self.info_detailed = []

        for place_id in self.businesses_ids:
            payload = {"place_id": place_id,
                       "key": self.api_key}
            self.info_detailed.append(requests.get(details_link, params=payload).json())

        # self.place_id = self.info.json()['results']['vicinity'][counter]['place_id']

    def _get_place_info_via_text(self, address):

        text_link = \
            "https://maps.googleapis.com/maps/api/place/textsearch/json?"

        payload = {"query": address,
                   "key": self.api_key}

        self.info_text = requests.get(text_link, params=payload)

if __name__ == '__main__':
    place = GooglePlaces(internal_api_key="GOOGLE")
    place.fetch_info(address='3000 lawrence street denver 80205')
    print(len(place.info_detailed))
    print(place.fetch_relevant_info())
