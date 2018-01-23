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

    def fetch_info(self, address):

        self._get_place_info_via_text(address=address)
        self._get_place_info(address=address)
        self._get_details(address=address)

    def fetch_relevant_info(self):
        dct = {}
        topic_list = ['types', 'name', 'website', 'formatted_phone_number', 'price_level', 'rating']
        for i in range(len(self.info_detailed)):
            dct[i] = {}
            for topic in topic_list:
                try:
                    self.info_detailed[i]['result'][topic]

                except KeyError:
                    pass

                else:
                    dct[i][topic] = self.info_detailed[i]['result'][topic]
        return dct

    def _get_meta_data(self, address):

        """
        -- Get meta data --

            PARAMETERS
            ----------
                address: str
                    "2801 ash st denver co 80207"

                API: str
                    The API key to make the call to google street view

            RETURNS
            -------
                requests.get: json
                    jsonified meta data
        """

        payload = {"location": address,
                   "key": self.api_key}

        meta_data_link = \
            "https://maps.googleapis.com/maps/api/streetview/metadata?"

        self.meta_data_json_object = requests.get(meta_data_link, params=payload)

        lat = self.meta_data_json_object.json()['location']['lat']
        lng = self.meta_data_json_object.json()['location']['lng']

        return lat, lng

    def _api(self, api):
        place_api = {'details':
                     "https://maps.googleapis.com/maps/api/place/details/json?",
                     'nearby':
                     "https://maps.googleapis.com/maps/api/place/nearbysearch/json?",
                     'text':
                     "https://maps.googleapis.com/maps/api/place/textsearch/json?",
                     'meta_data':
                     "https://maps.googleapis.com/maps/api/streetview/metadata?"
                     }
        return place_api[api]

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

    def _get_place_info(self, address, radius=5):
        lat, lng = self._get_meta_data(address=address)

        place_link = \
            "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"

        payload = {"location": "{},{}".format(lat, lng),
                   "key": self.api_key,
                   "radius": radius}

        self.info_radius = requests.get(place_link, params=payload)

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
