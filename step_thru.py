# @Author: Benjamin R. Everett <beneverett>
# @Date:   01-24-2018
# @Email:  benjamin.r.everett@gmail.com
# @Filename: step_thru.py
# @Last modified by:   beneverett
# @Last modified time: 01-24-2018

from google_places import HitGooglePlacesAPI

place = HitGooglePlacesAPI(internal_api_key="GOOGLE")

place_1 = (39.778762, -104.879870)
place_2 = (39.744255, -104.942354)

step_thru = 0.000100
counter = 0

current_location = place_2
results = []
while place_1[0] > place_2[0]:
    print(current_location)
    place.fetch_radius_info(lat_lng=current_location)
    num = len(place.radius_response.json()['results'])
    results.append(num)
    current_location = (current_location[0] + step_thru, current_location[1])
    counter += 1
    print("Fetch number: ", counter)
    print("Number businesses: ", sum(results))
