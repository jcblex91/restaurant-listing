from django.shortcuts import render
import os
import sys
import json
import time as dt
import requests
import configparser
from zomathon import ZomatoAPI
from .models import ZomatoRestaurants,GoogleRestaurants,RestaurantTimings
from .forms import AggregateForm
from django.db.models import Q


from django.http import HttpResponse
from datetime import datetime, time
from django.conf import settings




# Config
config = configparser.ConfigParser()
config.read('config.ini')



# TEST




def test(request):

    timing_obj = RestaurantTimings.objects.filter(restaurant_id=7)
    todays_weekday = datetime.today().isoweekday()
    today_open_time = ""
    today_close_time = ""

    for item_timing_obj in timing_obj:
        if(item_timing_obj.day == todays_weekday):
            today_open_time = item_timing_obj.open_time
            today_close_time = item_timing_obj.close_time


    today_open_time = datetime.strptime(today_open_time,'%I:%M %p')
    today_close_time = datetime.strptime(today_close_time,'%I:%M %p')


    open_hour = today_open_time.hour
    open_minute = today_open_time.minute

    close_hour = today_close_time.hour
    close_minute = today_close_time.minute

    #
    # print("Working Hours: "+ str(today_open_time) + " - " + str(today_close_time))

    # print(is_time_between(time(10, 30), time(22, 30)))
    open = is_time_between(time(open_hour, open_minute), time(close_hour, close_minute))
    if(open == 'TRUE'):
        print("Open")
    else:
        print("Closed")

def landing(request):
    if request.method == 'POST':
        print("Submitted")
        form = AggregateForm(request.POST)
        if form.is_valid():
            print("Passed")
            lat=request.POST['lat']
            print("Lat: ",lat)
    else:
        form = AggregateForm()
    return render(request, 'landing.html', {'form': form})






def ZomatoCollect(request):
    lat = 12.9726518
    long = 77.6067523
    print(lat,long)
    ZomatoRestaurantImport(lat,long)
    print("ZOMATO OVER")
    return home(request)

def GoogleCollection(request):


    latitude = 13.083366
    longitude = 80.270835
    radius_in_mtrs = 5000

    # print("+++++++++++++++++++++++++++++++STARTED GOOGLE ESTABLISHMENTS+++++++++++++++++++++++++++++++")
    # GoogleEstablishmentsCollection(latitude,longitude,radius_in_mtrs)
    print("+++++++++++++++++++++++++++++++STARTED GOOGLE PLACE DETAILS+++++++++++++++++++++++++++++++")
    GooglePlaceDetailsCollection()
    print("+++++++++++++++++++++++++++++++STARTED MAP QUEST+++++++++++++++++++++++++++++++")
    MapQuestAPI()
    print("+++++++++++++++++++++++++++++++STARTED URL SHORTENER+++++++++++++++++++++++++++++++")
    UrlShortener()
    print("+++++++++++++++++++++++++++++++STARTED GOOGLE PHOTO COLLECTION+++++++++++++++++++++++++++++++")
    GooglePlacePhotoCollection()
    print("OVER!!!")

    return home(request)



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
        id = google_restaurant_entries_item.id
        name = google_restaurant_entries_item.name
        types = google_restaurant_entries_item.types
        rating = google_restaurant_entries_item.rating
        price_level = google_restaurant_entries_item.price_level
        vicinity = google_restaurant_entries_item.vicinity
        address = google_restaurant_entries_item.address
        contact = google_restaurant_entries_item.contact
        website = google_restaurant_entries_item.website
        lat = google_restaurant_entries_item.lat
        long = google_restaurant_entries_item.long
        place_url = google_restaurant_entries_item.place_url
        timings = google_restaurant_entries_item.timings

        if(len(str(website)) > 38):
            website = google_restaurant_entries_item.short_url

        image = google_restaurant_entries_item.photo_url

        google_restaurant_dict["lat"] = lat
        google_restaurant_dict["long"] = long
        google_restaurant_dict["name"] = name
        google_restaurant_dict["types"] = types
        google_restaurant_dict["rating"] = rating
        google_restaurant_dict["price_level"] = price_level
        if((len(str(vicinity)) > 39) and (len(str(address))) < len(str(vicinity))):
            google_restaurant_dict["vicinity"] = address
        else:
            google_restaurant_dict["vicinity"] = address
        google_restaurant_dict["contact"] = contact
        google_restaurant_dict["website"] = website
        google_restaurant_dict["image"] = image
        maps_api = "http://www.google.com/maps/place/{lat},{long}/@{lat},{long},20z"
        if(str(place_url) == '-1'):
            maps_api_query = maps_api.format(lat = lat,long = long)
            google_restaurant_dict["place_url"] = maps_api_query

        else:
            google_restaurant_dict["place_url"] = place_url

        # Check If the Restaurant Is OPEN or CLOSED right NOW
        if(timings == 0):
            google_restaurant_dict["open_now"] = 1
        elif(timings == 1):
            google_restaurant_dict["open_now"] = is_restaurant_open(id)
        else:
            google_restaurant_dict["open_now"] = 2

        google_restaurants_list.append(google_restaurant_dict.copy())
        google_restaurant_dict.clear()

    return render(request, 'index.html',{'restaurants_list':google_restaurants_list})


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


# REFINED Google API CALLS


def GoogleEstablishmentsCollection(latitude,longitude,radius_in_kms):
    lat = latitude
    long = longitude
    print(lat, long)
    key = config['GoogleAPI']['api_key']
    radius = radius_in_kms
    type = 'restaurant'
    keyword = ''

    places_details_api_count = 0

    query_string_structure = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{long}&radius={radius}&type={type}&keyword={keyword}&key={api_key}"
    query_string = query_string_structure.format(lat=lat, long=long, radius=radius, type=type, keyword=keyword,
                                                 api_key=key)
    response = requests.get(query_string)
    json_data = json.loads(response.text)

    next_page_token = ""
    next_page_flag = 1
    first_page_flag = 1

    try:
        while (next_page_flag):
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

                        if 'photos' in item:
                            photo_reference_string = (item["photos"])
                            for item_photo in photo_reference_string:
                                photo_reference = item_photo["photo_reference"]
                        else:
                            photo_reference = "Blank"

                        entry = GoogleRestaurants(
                            name=name,
                            reference=reference,
                            types=types,
                            google_place_id=place_id,
                            rating=rating,
                            user_ratings_total=user_ratings_total,
                            price_level=price_level,
                            contact=-1,
                            website=-1,
                            short_url=-1,
                            place_url=-1,
                            vicinity=vicinity,
                            lat=lat,
                            long=lng,
                            photo_ref=photo_reference,
                            photo_url=-1)
                        entry.save()
                        print(name, " is saved @ ", entry.id)

            else:
                query_string_structure = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken={next_page_token}&key={api_key}"
                query_string = query_string_structure.format(next_page_token=next_page_token, api_key=key)
                dt.sleep(30)
                print("Next Page")
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

                        if 'photos' in item:
                            photo_reference_string = (item["photos"])
                            for item_photo in photo_reference_string:
                                photo_reference = item_photo["photo_reference"]
                        else:
                            photo_reference = "Blank"

                        entry = GoogleRestaurants(
                            name=name,
                            reference=reference,
                            types=types,
                            google_place_id=place_id,
                            rating=rating,
                            user_ratings_total=user_ratings_total,
                            price_level=price_level,
                            contact=-1,
                            website=-1,
                            short_url=-1,
                            place_url=-1,
                            vicinity=vicinity,
                            lat=lat,
                            long=lng,
                            photo_ref=photo_reference,
                            photo_url=-1)

                        entry.save()
                        print(name, " is saved @ ", entry.id)
                        if ('next_page_token' in json_data):
                            next_page_token = json_data["next_page_token"]
                        else:
                            next_page_flag = 0

    except Exception as e:
        print("error", e)

def GooglePlaceDetailsCollection():
    key = config['GoogleAPI']['api_key']
    place_details_query = "https://maps.googleapis.com/maps/api/place/details/json?placeid={place_id}&key={api_key}"
    places = GoogleRestaurants.objects.filter(Q(contact=-1 or 0) | Q(website=-1 or 0) | Q(place_url=-1 or 0) |
                                              Q(timings=-1 or 0))
    for place_item in places:
        pk = place_item.id
        place_name = place_item.name
        place_id = place_item.google_place_id
        place_details_query_string = place_details_query.format(place_id=place_id, api_key=key)
        print(pk, " - ", place_item.name, " - ", place_id)
        print(place_details_query_string)

        try:
            place_details_response = requests.get(place_details_query_string, stream=True)
            place_details_json_data = json.loads(place_details_response.text)
            place_details_json_data_result = place_details_json_data["result"]

            if 'url' in place_details_json_data_result:
                place_url = str(place_details_json_data_result["url"])
            else:
                place_url = 0

            if 'international_phone_number' in place_details_json_data_result:
                international_phone_number = str(place_details_json_data_result["international_phone_number"])
            else:
                international_phone_number = 0

            if 'website' in place_details_json_data_result:
                website = str(place_details_json_data_result["website"])
            else:
                url = "https://www.google.com/maps/search/?api=1&query={place_name}&query_place_id={place_id}"
                place_name_url_encoded = place_name.replace(" ", "+")
                url_query_string = url.format(place_id=place_id, place_name=place_name_url_encoded)
                print(url_query_string)
                website = url_query_string

            if 'opening_hours' in place_details_json_data_result:
                opening_hours = place_details_json_data_result["opening_hours"]["periods"]
                count_opening_hours = len(opening_hours)
                if(count_opening_hours == 1):
                    timing_entry_id = 0
                else:
                    for item_opening_hours in opening_hours:
                        dow = item_opening_hours['open']['day']
                        open_time = item_opening_hours['open']['time']
                        close_time = item_opening_hours['close']['time']

                        open_time = open_time[:2] + ':' + open_time[2:]
                        close_time = close_time[:2] + ':' + close_time[2:]

                        ot = dt.strptime(open_time, "%H:%M")
                        open_time = dt.strftime("%I:%M %p", ot)


                        ct = dt.strptime(close_time, "%H:%M")
                        close_time = dt.strftime("%I:%M %p", ct)

                        timing_entry = RestaurantTimings(day = int(dow),open_time = open_time,
                                                         close_time = close_time,restaurant_id = pk )
                        timing_entry.save()

                        print(str(dow) + " - " + str(open_time) + " - " + str(close_time))
                        timing_entry_id = 1
            else:
                timing_entry_id = 2
            obj = GoogleRestaurants.objects.get(pk=pk)
            obj.contact = international_phone_number
            obj.website = website
            obj.place_url = place_url
            obj.timings = timing_entry_id
            obj.save()

            print(place_item.name, "is updated")
        except Exception as e:

            print("Place Details API failed!", e)
            international_phone_number = 0
            website = 0

        print("Waiting...")
        dt.sleep(60)

def GooglePlacePhotoCollection():
    key = config['GoogleAPI']['api_key']
    places = GoogleRestaurants.objects.filter(photo_url=-1)
    photo_details_query = "https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={api_key}"
    save_path = settings.MEDIA_ROOT + '/google_place_images'
    db_save_path = '/media/google_place_images/'
    while(places.count()):
        photo_count = places.count()
        for place_item in places:
            print("Photos left for grabbing:",photo_count)
            print("Currently grabbing: ", place_item.name)
            pk = place_item.id
            place_id = place_item.google_place_id
            file_name = str(place_id)
            photo_url = db_save_path + "/" + file_name

            photo_reference = place_item.photo_ref
            photo_details_query_string = photo_details_query.format(photo_ref=photo_reference,
                                                                    api_key=key)
            try:
                file_save_path = str(save_path + '/' + file_name)
                photo_details_response = requests.get(photo_details_query_string, stream=True)
                open(file_save_path, 'wb').write(photo_details_response.content)
                file_size = os.path.getsize(file_save_path)
                if (file_size > 4038):
                    obj = GoogleRestaurants.objects.get(pk=pk)
                    obj.photo_url = photo_url
                    obj.save()
                    print(place_item.name, "photo is updated")
                else:
                    os.remove(file_save_path)
                    print("Couldn't grab image of " + place_item.name)
            except Exception as e:

                print("Photo Details API failed!", e)
                international_phone_number = 0
                website = 0

            print("Waiting...")
            dt.sleep(60)
            photo_count = photo_count - 1
        places = GoogleRestaurants.objects.filter(photo_url=-1)
        print(">>>>>>>>>>>>>>>>>>>New Cycle Starts...")


def UrlShortener():

    bitly_query = "https://api-ssl.bitly.com/v3/shorten?access_token={access_token}&longUrl={long_url}"
    access_token = config['bitly']['access_token']
    places = GoogleRestaurants.objects.filter(short_url='-1').exclude(website='-1' or '0')
    try:
        for item_place in places:
            pk = item_place.id
            url = str(item_place.website)
            if (url == '0' or url == '1'):
                pass
            else:
                long_url = bitly_url_parse(url)
                bitly_query_string = bitly_query.format(access_token=access_token, long_url=long_url)
                bitly_response = requests.get(bitly_query_string)
                json_data = json.loads(bitly_response.text)
                bitly_data = json_data["data"]
                print(long_url + "-" + bitly_data["url"])

                obj = GoogleRestaurants.objects.get(pk=pk)
                obj.short_url = bitly_data["url"]
                obj.save()

    except Exception as e:
        print("error", e)

def MapQuestAPI():

    mapquest_query = "http://www.mapquestapi.com/geocoding/v1/reverse?key={access_token}&location={lat},{long}&includeRoadMetadata=true&includeNearestIntersection=true"
    access_token = config['mapquest']['consumer_key']
    places = GoogleRestaurants.objects.filter(address='-1')
    try:
        for item_place in places:
            pk = item_place.id
            lat = str(item_place.lat)
            long = str(item_place.long)
            mapquest_query_string = mapquest_query.format(access_token=access_token, lat=lat, long=long)
            mapquest_response = requests.get(mapquest_query_string)
            json_data = json.loads(mapquest_response.text)
            mapquest_result = json_data["results"]
            for item_mapquest_result in mapquest_result:
                mapquest_locations = item_mapquest_result["locations"]
            for item_mapquest_locations in mapquest_locations:
                street = item_mapquest_locations["street"]
                area = item_mapquest_locations["adminArea5"]
                state = item_mapquest_locations["adminArea3"]

                if (len(str(street)) == 0):
                    if (len(str(area)) == 0):
                        if (len(str(state)) != 0):
                            address = str(state)
                        else:
                            address = "Not Available!"
                    else:
                        if ((len(str(area)) + len(str(state))) > 38):
                            address = str(area)
                        else:
                            address = str(area) + "," + str(state)
                else:
                    if ((len(str(street)) + len(str(area))) > 38):
                        address = str(street)
                    else:
                        address = str(street) + "," + str(area)

                # address = str(street)+","+str(area)

                obj = GoogleRestaurants.objects.get(pk=pk)
                obj.address = str(address)
                obj.save()

    except Exception as e:
        print("error", e)

def bitly_url_parse(url):
    url = url.replace(" ", "%20")
    url = url.replace("!", "%21")
    url = url.replace("#", "%23")
    url = url.replace("$", "%24")
    url = url.replace("&", "%26")
    url = url.replace("'", "%27")
    url = url.replace("(", "%28")
    url = url.replace(")", "%29")
    url = url.replace("*", "%2A")
    url = url.replace("+", "%2B")
    url = url.replace(",", "%2C")
    url = url.replace("/", "%2F")
    url = url.replace(":", "%3A")
    url = url.replace(";", "%3B")
    url = url.replace("=", "%3D")
    url = url.replace("?", "%3F")
    url = url.replace("@", "%40")
    url = url.replace("[", "%5B")
    url = url.replace("]", "%5D")

    return url

def is_restaurant_open(restaurant_id):
    timing_obj = RestaurantTimings.objects.filter(restaurant_id=restaurant_id)
    todays_weekday = datetime.today().isoweekday()
    today_open_time = ""
    today_close_time = ""

    for item_timing_obj in timing_obj:
        if(item_timing_obj.day == todays_weekday):
            today_open_time = str(item_timing_obj.open_time)
            today_close_time = str(item_timing_obj.close_time)


    # print("Open Time: "+ today_open_time)
    # print("Close Time: "+ today_close_time)
    today_open_time = datetime.strptime(today_open_time,'%I:%M %p')
    today_close_time = datetime.strptime(today_close_time,'%I:%M %p')




    # open_hour = today_open_time.hour
    # open_minute = today_open_time.minute

    open_hour = today_open_time.hour
    if(open_hour == 0):
        open_hour = 24
    open_minute = today_open_time.minute

    close_hour = today_close_time.hour
    if(close_hour == 0):
        close_hour = 24
    close_minute = today_close_time.minute

    # print("Open Hr::",open_hour)
    # print("Open Mts::",open_minute)
    #
    # print("Close Hr::",close_hour)
    # print("Close Mts::",close_minute)


    #
    # print("Working Hours: "+ str(today_open_time) + " - " + str(today_close_time))

    # print(is_time_between(time(10, 30), time(22, 30)))

    open = is_time_between(open_hour,open_minute,close_hour,close_minute)
    if(open == 1):
        return 1
    else:
        return 0

def is_time_between(open_hour,open_minute,close_hour,close_minute):
    current_time = datetime.now().time()
    # print("Open Hour: "+str(open_hour))
    # print("Open Minute: "+str(open_minute))
    # print("Close Hour: "+str(close_hour))
    # print("Close Minute: "+str(close_minute))
    # print("Current Hour:"+str(current_time.hour))
    # print("Current Time:"+str(current_time))


    if (current_time.hour == 0):

        if open_hour < close_hour:
            if open_hour < 24 and current_time.hour < close_hour:
                return 1
            elif open_hour == 24:
                if current_time.minute >= open_minute:
                    return 1
                else:
                    return 0
            elif close_hour == 24:
                if current_time.minute >= close_minute:
                    return 0
                else:
                    return 1
    else:

        if open_hour < close_hour:
            if current_time.hour > open_hour and current_time.hour < close_hour:
                return 1
            elif current_time.hour == open_hour:
                if current_time.minute >= open_minute:
                    return 1
                else:
                    return 0
            elif current_time.hour == close_hour:
                if current_time.minute >= close_minute:
                    return 0
                else:
                    return 1






