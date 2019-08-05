from googleplaces import GooglePlaces, types, lang
import json
import requests

# Global Variables
restaurants_list = []
restaurant_dict = {}

name = ""
zomato_id = ""
cuisines = ""
featured_image = ""
average_cost_for_two = ""
thumb = ""
aggregate_rating = ""
rating_text = ""


key = 'AIzaSyAewpBVsVvZLsLBtYdU6rmwhLC2PIoaygY'
coordinate = {}
lat = 9.5925963
long = 76.5201203
radius = 10000
type = 'restaurant'
keyword = ''


query_string_structure = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{long}&radius={radius}&type={type}&keyword={keyword}&key={api_key}"
query_string = query_string_structure.format(lat=lat,long=long,radius=radius,type=type,keyword=keyword,api_key=key)
response = requests.get(query_string)
json_data = json.loads(response.text)

query_result = json_data["results"]
for item in query_result:
    place_id = item["place_id"]
    name = item["name"]
    if 'price_level' in item.values():
        price_level = item["price_level"]
    else:
        price_level = None
    reference = item["reference"]
    types = item["types"]
    rating = item["rating"]
    user_ratings_total = item["user_ratings_total"]

    restaurant_dict["place_id"]=place_id
    restaurant_dict["user_ratings_total"]=user_ratings_total
    restaurant_dict["name"]=name
    restaurant_dict["price_level"]=price_level
    restaurant_dict["rating"]=rating
    restaurant_dict["reference"]=reference
    restaurant_dict["types"]=types

    restaurants_list.append(restaurant_dict.copy())

print(restaurants_list)

# You may prefer to use the text_search API, instead.
# query_result = google_places.nearby_search(
#         lat_lng=coordinate,
#         radius=10000, types=[types.TYPE_RESTAURANT])
# query_result = google_places.radar_search(
#     lat_lng=coordinate,
#     radius=10000, types=[types.TYPE_RESTAURANT])
#
# print(query_result.places)
