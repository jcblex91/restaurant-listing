from django.shortcuts import render
import os
import sys
import json
import time
import requests
import configparser
from zomathon import ZomatoAPI
from .models import ZomatoRestaurants,GoogleRestaurants

from django.http import HttpResponse
from django.conf import settings



# Config
config = configparser.ConfigParser()
config.read('config.ini')


def test(request,username):

    query ="https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=CmRaAAAAGlCHo95krM3shML5XSgfDSN4xuFXY-0iOLHFmKF5Tr0kbOx8C4Rx7o0ThQkxy548-tFR0szvqJkPux6XijSPlPf9k4fTF3JOxHkO8ee47N4XnFJT4TbjIdZAQgJb80hVEhAZXUCOoe0YK-3BlBg9aJ76GhR4XuB1M2RhA-mSNvh3r0SVQnozqA&key=AIzaSyBnHtO72ujvlYnUUFeLEJiqL3LyziBGrag"
    # response = requests.get(query)
    save_path = settings.MEDIA_ROOT+'/google_place_images'
    file_name = 'kkhklgjhihkh8456r5g5f5t5'

    print(save_path)
    print(username)
    place_details_response = requests.get(query, stream=True)
    open(save_path + '/' + file_name, 'wb').write(place_details_response.content)

    image_data = open(save_path + '/' + file_name, "rb").read()

    return HttpResponse(image_data, content_type="image/png")



def home(request):

    # Global Variables
    zomato_restaurants_list = []
    zomato_restaurant_dict = {}
    google_restaurants_list = []
    google_restaurant_dict = {}

    name = ""
    zomato_id = ""
    cuisines = ""
    featured_image = ""
    average_cost_for_two = ""
    thumb = ""
    aggregate_rating = ""
    rating_text = ""

    zomato_restaurant_entries = ZomatoRestaurants.objects.all()
    for zomato_restaurant_entries_item in zomato_restaurant_entries:
        name = zomato_restaurant_entries_item.name
        zomato_id = zomato_restaurant_entries_item.zomato_id
        cuisines = zomato_restaurant_entries_item.cuisines
        featured_image = zomato_restaurant_entries_item.featured_image
        average_cost_for_two = zomato_restaurant_entries_item.average_cost_for_two
        thumb = zomato_restaurant_entries_item.thumb
        aggregate_rating = zomato_restaurant_entries_item.aggregate_rating
        rating_text = zomato_restaurant_entries_item.rating_text

        zomato_restaurant_dict["name"] = name
        zomato_restaurant_dict["zomato_id"] = zomato_id
        zomato_restaurant_dict["cuisines"] = cuisines
        zomato_restaurant_dict["featured_image"] = featured_image
        zomato_restaurant_dict["average_cost_for_two"] = average_cost_for_two
        zomato_restaurant_dict["thumb"] = thumb
        zomato_restaurant_dict["aggregate_rating"] = aggregate_rating
        zomato_restaurant_dict["rating_text"] = rating_text

        zomato_restaurants_list.append(zomato_restaurant_dict.copy())
        zomato_restaurant_dict.clear()

    google_restaurant_entries = GoogleRestaurants.objects.all()
    for google_restaurant_entries_item in google_restaurant_entries:
        name = google_restaurant_entries_item.name
        reference = google_restaurant_entries_item.reference
        types = google_restaurant_entries_item.types
        google_place_id = google_restaurant_entries_item.google_place_id
        rating = google_restaurant_entries_item.rating
        price_level = google_restaurant_entries_item.price_level
        vicinity = google_restaurant_entries_item.vicinity
        contact = google_restaurant_entries_item.contact
        website = google_restaurant_entries_item.website

        google_restaurant_dict["name"] = name
        google_restaurant_dict["reference"] = reference
        google_restaurant_dict["types"] = types
        google_restaurant_dict["google_place_id"] = google_place_id
        google_restaurant_dict["rating"] = rating
        google_restaurant_dict["price_level"] = price_level
        google_restaurant_dict["vicinity"] = vicinity
        google_restaurant_dict["contact"] = contact
        google_restaurant_dict["website"] = website

        google_restaurants_list.append(google_restaurant_dict.copy())
        google_restaurant_dict.clear()



    return render(request, 'index.html',{'restaurants_list':zomato_restaurants_list})

def collection(request):
    lat = 8.565128
    long = 76.8504593
    print(lat,long)
    ZomatoRestaurantImport(lat,long)
    print("ZOMATO OVER")
    GoogleRestaurantImport(lat,long)
    return home(request)


def ZomatoRestaurantImport(lat,long):
    API_KEY = config['zomato']['api_key']
    zom = ZomatoAPI(API_KEY)

    # Find the nearby restaurant
    coordinate = "{lat} {lon}".format(lat=lat, lon=long)
    nearby = zom.geocode(coordinate=coordinate)

    try:
        nearby_restaurants = nearby["nearby_restaurants"]
        for item_nearby_restaurants in nearby_restaurants:
            restaurant = item_nearby_restaurants["restaurant"]

# Check if the resaturant already exist in db
            num_results = ZomatoRestaurants.objects.filter(zomato_id=restaurant["id"]).count()
            if(num_results == 0):
                user_rating = restaurant["user_rating"]
                location =  restaurant["location"]
                entry = ZomatoRestaurants(name=restaurant["name"],
                                          zomato_id=restaurant["id"],
                                          cuisines=restaurant["cuisines"],
                                          featured_image=restaurant["featured_image"],
                                          average_cost_for_two=restaurant["average_cost_for_two"],
                                          thumb=restaurant["thumb"],
                                          aggregate_rating=user_rating["aggregate_rating"],
                                          rating_text=user_rating["rating_text"],
                                          votes=user_rating["votes"],
                                          lat = location["latitude"],
                                          long = location["longitude"])
                entry.save()


    except Exception as e:
        print("error", e)

def GoogleRestaurantImport(lat,long):
    key = config['GoogleAPI']['api_key']
    radius = 15000
    type = 'restaurant'
    keyword = ''

    places_details_api_count = 0

    query_string_structure = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{long}&radius={radius}&type={type}&keyword={keyword}&key={api_key}"
    query_string = query_string_structure.format(lat=lat, long=long, radius=radius, type=type, keyword=keyword,
                                                 api_key=key)
    print("Response #1")
    response = requests.get(query_string)
    json_data = json.loads(response.text)

    next_page_token=""
    next_page_flag=1
    first_page_flag = 1

    try:
        while(next_page_flag):
            if (first_page_flag == 1):
                first_page_flag = 0
                if ('next_page_token' in json_data):
                    next_page_token = json_data["next_page_token"]
                query_result = json_data["results"]
                for item in query_result:
                    num_results = GoogleRestaurants.objects.filter(google_place_id=str(item["place_id"])).count()
                    if (num_results == 0):
                        place_id = str(item["place_id"])

                        name = str(item["name"])
                        if 'price_level' in item:
                            price_level = str(item["price_level"])
                        else:
                            price_level = 0.0

                        if 'reference' in item:
                            reference = str(item["reference"])
                        else:
                            reference = 0

                        if 'types' in item:
                            types = str(item["types"])
                        else:
                            types = 0

                        if 'rating' in item:
                            rating = str(item["rating"])
                        else:
                            rating = 0

                        if 'user_ratings_total' in item:
                            user_ratings_total = str(item["user_ratings_total"])
                        else:
                            user_ratings_total = 0

                        if 'vicinity' in item:
                            vicinity = str(item["vicinity"])
                        else:
                            vicinity = 0

                        lng = str(item["geometry"]["location"]["lng"])
                        lat = str(item["geometry"]["location"]["lat"])
                        photo_reference = ""
                        photo_reference_string = (item["photos"])
                        for item_photo in photo_reference_string:
                            photo_reference = item_photo["photo_reference"]


                        # PLACE DETAILS API
                        time.sleep(30)
                        try:
                            place_details_response = place_details_api(place_id)
                            place_details_json_data = json.loads(place_details_response.text)
                            place_details_json_data_result = place_details_json_data["result"]

                            if 'international_phone_number' in place_details_json_data_result:
                                international_phone_number = str(
                                    place_details_json_data_result["international_phone_number"])
                            else:
                                international_phone_number = 0

                            if 'website' in place_details_json_data_result:
                                website = str(place_details_json_data_result["website"])
                            else:
                                website = 0

                        except Exception as e:

                            print("Place Details API failed!", e)
                            international_phone_number = 0
                            website = 0

                        finally:
                            # Place Photo API
                            time.sleep(30)
                            photo_details_query = "https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={api_key}"
                            photo_details_query_string = photo_details_query.format(photo_ref=photo_reference,
                                                                                    api_key=key)
                            save_path = settings.MEDIA_ROOT + '/google_place_images'
                            file_name = str(place_id)

                            print("Response #3")
                            place_details_response = requests.get(photo_details_query_string, stream=True)
                            open(save_path + '/' + file_name, 'wb').write(place_details_response.content)

                            entry = GoogleRestaurants(
                                name=name,
                                reference=reference,
                                types=types,
                                google_place_id=place_id,
                                rating=rating,
                                user_ratings_total=user_ratings_total,
                                price_level=price_level,
                                contact=international_phone_number,
                                website=website,
                                vicinity="TEST",
                                lat=lat,
                                long=lng,
                                photo_url=photo_reference)
                            entry.save()




            else:
                query_string_structure = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken={next_page_token}&key={api_key}"
                query_string = query_string_structure.format(next_page_token=next_page_token, api_key=key)
                time.sleep(30)
                print("Response #4")
                response = requests.get(query_string)
                places_details_api_count = places_details_api_count + 1
                json_data = json.loads(response.text)
                query_result = json_data["results"]

                for item in query_result:
                    num_results = GoogleRestaurants.objects.filter(google_place_id=str(item["place_id"])).count()
                    if (num_results == 0):

                        place_id = str(item["place_id"])
                        name = str(item["name"])
                        if 'price_level' in item:
                            price_level = str(item["price_level"])
                        else:
                            price_level = 0.0

                        if 'reference' in item:
                            reference = str(item["reference"])
                        else:
                            reference = 0

                        if 'types' in item:
                            types = str(item["types"])
                        else:
                            types = 0

                        if 'rating' in item:
                            rating = str(item["rating"])
                        else:
                            rating = 0

                        if 'user_ratings_total' in item:
                            user_ratings_total = str(item["user_ratings_total"])
                        else:
                            user_ratings_total = 0

                        if 'vicinity' in item:
                            vicinity = str(item["vicinity"])
                        else:
                            vicinity = 0

                        lng = str(item["geometry"]["location"]["lng"])
                        lat = str(item["geometry"]["location"]["lat"])
                        photo_reference = ""
                        photo_reference_string = (item["photos"])
                        for item_photo in photo_reference_string:
                            photo_reference = item_photo["photo_reference"]

                        # PLACE DETAILS API
                        time.sleep(30)
                        place_details_query ="https://maps.googleapis.com/maps/api/place/details/json?placeid={place_id}&key={api_key}"
                        place_details_query_string = place_details_query.format(place_id=place_id,api_key=key)
                        print("Response #5")
                        place_details_response = requests.get(place_details_query_string)
                        place_details_json_data = json.loads(place_details_response.text)

                        place_details_json_data_result = place_details_json_data["result"]


                        if 'international_phone_number' in place_details_json_data_result:
                            international_phone_number = str(place_details_json_data_result["international_phone_number"])
                        else:
                            international_phone_number = 0


                        if 'website' in place_details_json_data_result:
                            website = str(place_details_json_data_result["website"])
                        else:
                            website = 0

                        entry = GoogleRestaurants(
                            name=name,
                            reference=reference,
                            types=types,
                            google_place_id=place_id,
                            rating=rating,
                            user_ratings_total=user_ratings_total,
                            price_level=price_level,
                            contact= international_phone_number,
                            website = website,
                            vicinity="TEST",
                            lat = lat,
                            long = lng,
                            photo_url = photo_reference)

                        entry.save()
                        if ('next_page_token' in json_data):
                            next_page_token = json_data["next_page_token"]
                        else:
                            next_page_flag = 0

    except Exception as e:
        print("error",e)


def place_details_api(place_id):
    key = config['GoogleAPI']['api_key']
    place_details_query = "https://maps.googleapis.com/maps/api/place/details/json?placeid={place_id}&key={api_key}"
    place_details_query_string = place_details_query.format(place_id=place_id, api_key=key)
    place_details_response = requests.get(place_details_query_string, stream=True)

    print("API String: ",place_details_query_string)

    return place_details_response
