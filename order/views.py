from contextlib import _RedirectStream, redirect_stderr
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from order.models import BirdModel
import json
import requests
from django.http import JsonResponse


mypos = {'lat' : 22.63720862650741, 'lng' : 121.50426592818646}

def getMyloc(request):
    if request.method == "POST":
        #posJson = request.POST.get('posJson')
        posJson = json.loads(request.body.decode('utf-8'))
        #print(posJson)
        global mypos  #global
        mypos = posJson
        print('getMyloc')
        print(mypos)
        print(mypos.items())
        #print(request.body.decode('utf-8'))
        weather_msg = weather()
        myaddress = latlng_to_address(mypos)
        return JsonResponse({
                'message': 'success',
                'weather_msg': weather_msg,
                'myaddress' : myaddress
            })
    else:
        return JsonResponse({
                'message': 'error'
            })

### for test
@csrf_exempt
def test(request):
    global mypos  #global
    google_api_key = ' '
    recent_msg = recent()
    weather_msg = weather()
    myaddress = latlng_to_address(mypos)
    if request.method == "POST":
        weather_msg = weather()
        recent_msg = recent()
        print(mypos)
        myaddress = latlng_to_address(mypos)
        print(myaddress)
        if('distance_btn' in request.POST):
            loc2 = request.POST['loc2']
            print(loc2)
            if(myaddress == "" or loc2 == ""):
                distance_msg = 'error'
            elif(distance(myaddress, loc2) !=  'error'):
                distance_msg = distance(myaddress, loc2)
            else:
                distance_msg = 'error'
    return render(request,'test.html',locals())



def map(request):
    global mypos  #global
    google_api_key = ' '
    center_lan_lng ={ 'lat': 25.119136595732403, 'lng': 121.4708654841385 }#關渡自然公園
    #################
    #################
    ################# params: (origin_lan_lng, destination_lan_lng)
    origin_lan_lng ={'lat': mypos['lat'], 'lng':mypos['lng']}
    destination_lan_lng = {'lat': address_to_latlng('112台北市北投區關渡路55號')['lat'], 'lng': address_to_latlng('112台北市北投區關渡路55號')['lng']}
    #print(origin_lan_lng)
    #print(destination_lan_lng)
    return render(request,'map.html',locals())


def update_destination(request):
    new_location = request.POST.get('new_location')

    # 在這裡您可以處理新地點的相關邏輯，例如將地址轉換為經緯度等
    new_lat_lng = address_to_latlng(new_location)

    # 更新 destination_lan_lng 的值
    destination_lan_lng['lat'] = new_lat_lng['lat']
    destination_lan_lng['lng'] = new_lat_lng['lng']

    return JsonResponse({'message': '地點更新成功'})
### index
def index(request):
    google_api_key = ' '
    weather_msg = weather()
    if request.method == "POST":
        weather_msg = weather()
    return render(request,'index.html',locals())


#### about
def about(request):
    return render(request,'about/about.html')

def index_test(request):
    google_api_key = ' '
    weather_msg = weather()
    if request.method == "POST":
        weather_msg = weather()
    return render(request,'index_test.html',locals())



#### birdlist
def birdlist(request):
    return render(request,'birdlist/birdlist.html')

def birdinfo(request, sortType):
    birds = bList()
    return render(request,'birdlist/birdinfo.html', locals())
### guide
def guide(request):
    return render(request,'guide/guide.html')
def basicKnowledge(request):
    return render(request,'guide/basicKnowledge.html')
def development(request):
    return render(request,'guide/development.html')
def equipment(request):
    return render(request,'guide/equipment.html')
def ethics(request):
    return render(request,'guide/ethics.html')

### realtime
def realtime(request):
    recent_msg = recent()
    return render(request,'realtime/realtime.html',locals())



def info(request):
    return render(request,'realtime/info.html')
def place(request):
    return render(request,'realtime/place.html')
def recommend(request):
    return render(request,'realtime/recommend.html')
def TWmap(request):
    return render(request,'svgMap/TWmap.html')


### database
def order(request):
    if request.method == "POST":
        #鳥名稱相關
        name= request.POST['name']
        familyName  = request.POST['familyName']
        englishName  = request.POST['englishName']
        nickName  = request.POST['nickName']
        #鳥等級
        level  = request.POST['level']
        #鳥時間相關
        startMonth  = request.POST['startMonth']
        endMonth  = request.POST['endMonth']
        season  = request.POST['season']
        #鳥棲息地
        habitat  = request.POST['habitat']
        #鳥描述
        description  = request.POST['description']
        #鳥圖片相關

        image  = request.POST['image']
        photoby  = request.POST['photoby']

        unit = BirdModel.objects.create(
            name=name,
            familyName=familyName,
            englishName=englishName,
            nickName=nickName,

            level=level,

            startMonth=startMonth,
            endMonth=endMonth,
            season=season,

            habitat=habitat,

            description=description,

            image=image,
            photoby=photoby
            )
        unit.save()
    return render(request,'order.html',locals())

def upload_img(request):
    Birds = BirdModel.objects.all()
    #findname
    if request.method == 'POST':
        mname = request.POST['name']  # get name
        try :
            #資料表.objects.get(查詢條件)
            mbird = BirdModel.objects.get(name=mname)
            #修改
            mbird.photo = request.FILES.get('photo')
            mbird.save()  # save image
            return HttpResponse('成功新增'+mname+'照片')
        except:
            print('找不到'+mname)
    return render(request, 'upload_img.html',locals())

### 捨棄

#### weather_API
def weather():
    global mypos  #global
    my_address_components = get_administrative_area_level_1(mypos)
    print(str(my_address_components))
    for index in range(0,10):
        print(str(index))
        if((my_address_components[index]['types'] == [ "administrative_area_level_2", "political" ])
            or (my_address_components[index]['types'] == ['administrative_area_level_1', 'political'])):
            mytown = str(my_address_components[index]['long_name'])
            print(mytown)
            mytown = mytown.replace('台','臺')
            print(mytown)
            break
    url = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001"
    params = {
        "Authorization": "CWB-A38B5122-DF26-47EB-A652-1AD1A5643F5C",
        "locationName": mytown,
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = json.loads(response.text)
        location = data["records"]["location"][0]["locationName"]
        weather_elements = data["records"]["location"][0]["weatherElement"]
        weather_state = weather_elements[0]["time"][0]["parameter"]["parameterName"]
        rain_prob = weather_elements[1]["time"][0]["parameter"]["parameterName"]
        min_tem = weather_elements[2]["time"][0]["parameter"]["parameterName"]
        comfort = weather_elements[3]["time"][0]["parameter"]["parameterName"]
        max_tem = weather_elements[4]["time"][0]["parameter"]["parameterName"]

        weather_msg = {
            'location' : location,
            'weather_state': weather_state,
            'rain_prob':rain_prob,
            'min_tem':min_tem,
            'comfort':comfort,
            'max_tem':max_tem}

    return weather_msg


### ebird_API
def recent():
    regionCode = 'TW'
    url = "https://api.ebird.org/v2/data/obs/"+regionCode+"/recent"

    payload={}
    headers = {
    'X-eBirdApiToken': 'ihe647qob150'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    #print(response.text)
    json_to_dict_ebird = json.loads(response.text)

    #print(json_to_dict)
    recent_datas = json_to_dict_ebird

    return recent_datas

### google_API

###計算兩點距離
def distance(loc1,loc2):
    params = {
        'key':' ',
        'origins': loc1,
        'destinations': loc2,
        'mode': 'driving', # mode: walking , driving , bicycling , transit
        'avoid' : 'tolls|highways|ferries'}

    url = 'https://maps.googleapis.com/maps/api/distancematrix/json?'
    response = requests.get(url, params=params)

    #print(response.text)
    json_to_dict_google = json.loads(response.text)

    print(json_to_dict_google)
    errorMsg = "error"
    distance_datas = {
        #'destination_addresses' : json_to_dict_google['destination_addresses'][0],
        #'origin_addresses' : json_to_dict_google['origin_addresses'][0],
        'origin_addresses' : loc1,
        'destination_addresses' : loc2,
        'distance' : json_to_dict_google['rows'][0]['elements'][0]['distance']['text'],
        'duration': json_to_dict_google['rows'][0]['elements'][0]['duration']['text']}

    if(json_to_dict_google['status'] == "OK" and json_to_dict_google['rows'][0]['elements'][0]['status'] == "OK"):
        return distance_datas
    else:
        return errorMsg

def address_to_latlng(loc):
    params = {
        'key':' ',
        'address' : loc}
    url = 'https://maps.googleapis.com/maps/api/geocode/json?'
    response = requests.get(url, params=params)
    #print(response.text)
    json_to_dict_lat_lng = json.loads(response.text)
    lat_lng = {
        'lat' :json_to_dict_lat_lng['results'][0]['geometry']['location']['lat'],
        'lng' :json_to_dict_lat_lng['results'][0]['geometry']['location']['lng']
    }
    return lat_lng

def latlng_to_address(lat_lng):
    lat_lng_value = str(lat_lng['lat'])+','+str(lat_lng['lng'])
    params = {
        'key':' ',
        'latlng' : lat_lng_value,
        'language':'zh-TW'}
    url = 'https://maps.googleapis.com/maps/api/geocode/json?'
    response = requests.get(url, params=params)
    #print(response.text)
    json_to_dict_address = json.loads(response.text)
    address = json_to_dict_address['results'][0]['formatted_address']
    print(address)
    return address

def get_administrative_area_level_1(lat_lng):
    lat_lng_value = str(lat_lng['lat'])+','+str(lat_lng['lng'])
    params = {
        'key':' ',
        'latlng' : lat_lng_value,
        'language':'zh-TW'}
    url = 'https://maps.googleapis.com/maps/api/geocode/json?'
    response = requests.get(url, params=params)
    #print(response.text)
    json_to_dict_address = json.loads(response.text)
    address_components = json_to_dict_address['results'][0]['address_components']
    print(address_components)
    return address_components
