# @Author: Benjamin R. Everett <beneverett>
# @Date:   01-22-2018
# @Email:  benjamin.r.everett@gmail.com
# @Filename: google_places.py
# @Last modified by:   beneverett
# @Last modified time: 01-23-2018

import requests
import os


class HitGooglePlacesAPI(object):

    def __init__(self,
                 api_key=None,
                 internal_api_key=None):

        self.api_key = api_key
        self.internal_api_key = internal_api_key
        self.requested_info = None

    def fetch_metadata_info(self, address):
        self.meta_data_response = self._hit_api(api='meta_data',
                                                address=address)

    def fetch_radius_info(self, address, radius=100):
        lat_lng = self._get_lat_lng(address=address)
        self.radius_response = self._hit_api(api='radius',
                                             lat_lng=lat_lng,
                                             radius=radius)

    def fetch_detailed_info(self, address=None, place_id=None):
        if address:
            # take the number e.g. for '2801 ash st' we want '2801'
            num = address.split(' ')[0]
            self.fetch_radius_info(address=address)
            response = self.radius_response
            place_ids = [response.json()['results'][i]['place_id']
                         for i in range(len(response.json()['results']))
                         if response.json()['results'][i]['vicinity']
                         .split(' ')[0] == num]
            self.detailed_response = [self._hit_api(api='details',
                                                    place_id=i)
                                      for i in place_ids]
        else:
            self.detailed_response = self._hit_api(api='details',
                                                   place_id=place_id)

    def fetch_text_info(self, address):
        self.text_response = self._hit_api(api='text', address=address)
        return self.text_response

    def _hit_api(self,
                 api,
                 place_id=None,
                 lat_lng=(0, 0),
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
                          place_id,
                          lat_lng,
                          radius,
                          address):

        api_key = self.api_key
        if api_key is None:
            api_key = os.environ.get(self.internal_api_key)

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

    def _get_lat_lng(self, address):
        response = self._hit_api(api='meta_data',
                                 address=address)
        lat = response.json()['location']['lat']
        lng = response.json()['location']['lng']

        return lat, lng


if __name__ == '__main__':
    place = HitGooglePlacesAPI(internal_api_key="GOOGLE")
    place.fetch_metadata_info(address='5225 E 38th Ave, Denver, CO 80207')
    place.fetch_radius_info(address='5225 E 38th Ave, Denver, CO 80207')
    place.fetch_detailed_info(address='5225 E 38th Ave, Denver, CO 80207')
    place.fetch_detailed_info(place_id='ChIJU5jhOsN7bIcR-X_Al6v1LSY')
