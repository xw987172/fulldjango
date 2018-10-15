from django.shortcuts import render
import math
# Create your views here.
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from datetime import datetime
import json,time
from django.db import connection
def hello(request):
    data = {}
    data["time"] = str(datetime.now())
    data["props"] = {
        "author" : "xuwei",
        "desc" : "want to do something...",
        "time":"2018-09-12",
    }
    cursor = connection.cursor()
    cursor.execute("select * from spider.football order by section,score desc")
    rows = cursor.fetchall()
    cursor.close()
    comments = ["section","name","matchCount","winCount","equalCount","lossCount","goal","loss","pareWin","score"]
    members = list()
    for item in rows:
        line = dict()
        for i,val in enumerate(comments):
            line[val] = item[i]
        members.append(line)
    data["info"] = {
        "total":1000,
        "members":members,
    }
	# return JsonResponse(data)
    try:
    	func_name = request.GET["callback"]
    except:
        func_name = "callbackfunc"
    response = HttpResponse("%s(%s)" %(func_name,str(data)))
    # response["Access-Control-Allow-Origin"] = "*"
    # response["Access-Control-Allow-Methods"] = "POST,GET,OPTIONS"
    # response["Access-Control-Max-Age"] = "1000"
    # response["Access-Control-Allow-Headers"] = "*"
    return response

def today(request):
    result = dict()
    result["data"] = dict()
    result["status_code"] = 200
    result["msg"] = "today所有门店基本信息表"
    cursor  = connection.cursor()
    columns = [{"name":"店号"},{"name":"店名"},{"name":"所在省份"},{"name":"所在城市"},{"name":"所在区域"},{"name":"经纬度"}]
    result["data"]["columns"] = ["店号","店名","所在城市","经纬度"]
    result["data"]["items"] = list()
    cursor.execute("select shopid,name,city,location from spider.today")
    data = cursor.fetchall()
    cursor.close()
    keys = ["shopid","name","city","location"]
    items = list()
    for item in data:
        line = dict(zip(keys,item))
        items.append(line)
    result["data"]["items"] = items
    try:
        func_name = request.GET["callback"]
    except:
        func_name = "callbackfunc"
    response = HttpResponse("%s(%s)" %(func_name,str(result)))
    return response 

def test(response):
    return render("test.html")

def geo(request):
	return render(request,"geoIndex.html")

def transformLat(x, y):
    ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x))
    ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(y * math.pi) + 40.0 * math.sin(y / 3.0 * math.pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(y / 12.0 * math.pi) + 320 * math.sin(y * math.pi / 30.0)) * 2.0 / 3.0
    return ret


def transformLon(x, y):
    ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))
    ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(x * math.pi) + 40.0 * math.sin(x / 3.0 * math.pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(x / 12.0 * math.pi) + 300.0 * math.sin(x / 30.0 * math.pi)) * 2.0 / 3.0
    return ret


def delta(lat, lng):
    a = 6378245.0
    # a: 卫星椭球坐标投影到平面地图坐标系的投影因子
    ee = 0.00669342162296594323
    # ee: 椭球的偏心率
    dLat = transformLat(lng - 105.0, lat - 35.0)
    dLon = transformLon(lng - 105.0, lat - 35.0)
    radLat = lat / 180.0 * math.pi
    magic = math.sin(radLat)
    magic = 1 - ee * magic * magic
    sqrtMagic = math.sqrt(magic)
    dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * math.pi)
    dLon = (dLon * 180.0) / (a / sqrtMagic * math.cos(radLat) * math.pi)
    return dLat, dLon


def wgs2gcj(wgsLat, wgsLng):
    """
    WGS-84转成GCJ-02
    """
    lat, lng = delta(wgsLat, wgsLng)
    return str(wgsLng + lng)+','+str(wgsLat + lat)

def geoAdd(request):
	data = dict()
	if request.POST:
		data["store_code"] = request.POST["store_code"]
		data["store_name"] = request.POST["store_name"]
		data["location"] = request.POST["location"]
		x,y = data["location"].split(",")
		data["location"] = wgs2gcj(float(y),float(x))
		if request.POST["isat"]!="yes":
			return HttpResponse("请回到门店以后，重新打开该页面，填写店号.")
	cursor = connection.cursor()
	if bool(data["store_code"]) ==False:
		return HttpResponseRedirect("/geo/index/")
	cursor = connection.cursor()
	cursor.execute("replace into today.today(store_code,store_name,location) values('%s','%s','%s')" %(data["store_code"],data["store_name"],data["location"]))
	connection.commit()
	cursor.close()
	return HttpResponse("填写成功，感谢配合！")
