import hashlib
import json

from flask import Flask
# 请求
from flask import request
# 跨域
from flask_cors import CORS
#引用pymysql
import pymysql
import mysql

#解决时间序列化问题
from datetime import date, datetime

import random
import config
#redis 模块
import redis

class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


app=Flask(__name__)
cors = CORS(app)
# db = pymysql.Connect("localhost","root","root","mall")
@app.route("/")
def index():
    return "{a:1, b:2}"




@app.route('/user/login',methods=["POST"])
def login():
    phone=request.json.get("phone")
    password = request.json.get("password")
    password = hashlib.sha1(password.encode()).hexdigest()
    # cursor = db.cursor(pymysql.cursors.DictCursor)
    # cursor.execute("SELECT * FROM user where phone='"+phone+"'and password='"+password+"'")
    # cursor.execute(,(phone,password))

    data = mysql.doIt("SELECT * FROM user where phone='"+phone+"'and password='"+password+"'")
    # cursor.close();
    # print("Database version : %s " % data)
    #returnmsg = json.dumps(data, cls=CJsonEncoder)
    returnmsg = {'status':0, 'uid':1, 'desc':'登陆成功'}

    if(len(data)==0):
        returnmsg["status"]=1
        returnmsg["desc"] = "用户密码不匹配"
        returnmsg['uid'] =0
    else:
        returnmsg["uid"]= data[0]["uid"]
        returnmsg["info"]=data[0]
    return json.dumps(returnmsg,cls=CJsonEncoder)

@app.route('/user/getsms',methods=["POST"])
def getsms():
    phone= request.json.get("phone")
    #先数据库中查询是否在1分钟发过，以及把数据插入
    # cursor = db.cursor(pymysql.cursors.DictCursor)
    # cursor.execute('SELECT id from sms_fil WHERE phone=%s', phone)
    data = mysql.doIt("SELECT id from sms_fil WHERE phone='"+phone+"'")
    isnew=0
    if(len(data)!=0):
        isnew=data[0]

    num = str(random.randint(1000,9999))
    thistime =datetime.now()
    if(isnew==0):
        mysql.Excuit('INSERT INTO sms_fil (phone,code,ins_date) VALUES ("'+phone+'","'+num+'","'+thistime.strftime('%Y-%m-%d %H:%M:%S')+'")')
    else:
        mysql.Excuit('UPDATE sms_fil SET code="'+num+'",ins_date="'+thistime.strftime('%Y-%m-%d %H:%M:%S')+'" WHERE phone="'+phone+'"')

    returnmsg = {"status":0, "desc": "获取成功","code":num}
    return json.dumps(returnmsg)

#获得类别商品
@app.route('/goods/type_lists')
def get_type_lists():
    #查询分类
    # cursor = db.cursor(pymysql.cursors.DictCursor)
    # cursor.execute()
    types = mysql.doIt('SELECT type_id,type_name FROM goods_type_fil ORDER BY type_id')
    # cursor.close()
    #查询所有代售商品
    # cursor = db.cursor(pymysql.cursors.DictCursor)
    # cursor.execute()
    result = mysql.doIt("SELECT * FROM goods_fil where status=0")
    # cursor.close();
    for p in types:
        p["data"]=[one for one in result if one["type_id"]==p["type_id"]]
    return json.dumps(types, cls=CJsonEncoder)


#获取商品详情
@app.route('/goods/detail')
def get_good_detatil():
    id = request.args.get("id")
    detail = mysql.getOne("SELECT * FROM goods_fil WHERE goods_id="+id);
    banners = mysql.doIt("SELECT url FROM goods_banner_fil WHERE goods_id="+id+" and `show`=1 order by orderby" );
    comment = mysql.doIt("SELECT a.comment_id,a.content,b.avatar,b.`name`,a.ins_date FROM `goods_comment_fil` a LEFT JOIN `user` b on a.uid=b.uid where goods_id="+id+" and is_show=0 and parent_id=0 ORDER BY a.ins_date DESC LIMIT 0,3")
    comment_num =mysql.getOne("SELECT COUNT(*) as num FROM `goods_comment_fil` WHERE goods_id="+id+" and is_show=0 and parent_id=0")
    photos = mysql.doIt("SELECT a.url FROM `goods_comment_image_fil` as a LEFT JOIN `goods_comment_fil` as b on a.comment_id = b.comment_id where b.goods_id="+id+" and a.is_show = 0 limit 4");
    photos_num = mysql.getOne("SELECT count(*) as q FROM `goods_comment_image_fil` as a LEFT JOIN `goods_comment_fil` as b on a.comment_id = b.comment_id where b.goods_id="+id+" and a.is_show = 0 limit 4")
    picdetail= mysql.doIt("SELECT url FROM goods_detail WHERE goods_id="+id+" order by orderby")
    returnmsg = {"detail": detail, "picdetail": picdetail, "banners": banners,"comment": comment, "photos": photos, "num": {"comment_num": comment_num["num"], "photos_num": photos_num["q"]}}

    return returnmsg

#获取商品收藏状态
@app.route("/goods/goods_favor_detail")
def goods_favor_detail():
    goodsid =request.args.get("goodsid")
    uid = request.args.get("uid")
    result = mysql.getOne("SELECT 1 as p FROM goods_favor_fil WHERE goods_id="+goodsid+" and uid="+uid+" and is_favor=0 LIMIT 1")
    #result = mysql.getOne(
    #    "SELECT count(*) as q FROM `goods_comment_image_fil` as a LEFT JOIN `goods_comment_fil` as b on a.comment_id = b.comment_id where b.goods_id=" + uid + " and a.is_show = 0 limit 4")
    returnmsg = {"favor": result}
    return returnmsg

#收藏商品或取消收藏
@app.route("/goods/favor")
def favor():
    goodsid = request.args.get("goodsid")
    uid = request.args.get("uid")
    is_favor = request.args.get("is_favor")
    thistime = datetime.now()
    result =mysql.getOne("SELECT 1 as p FROM goods_favor_fil WHERE goods_id="+goodsid+" and uid="+uid+" LIMIT 1")
    if int(is_favor) == 0:   #收藏
        if result == None:
            mysql.Excuit("INSERT goods_favor_fil (goods_id, uid, is_favor, ins_date) VALUES ("+goodsid+","+uid+","+is_favor+","+thistime.strftime('%Y-%m-%d %H:%M:%S')+")")
        else:
            mysql.Excuit("UPDATE goods_favor_fil SET is_favor="+is_favor+"  where goods_id="+goodsid+" and uid="+uid)
    else:   #不收藏
        mysql.Excuit("UPDATE goods_favor_fil SET is_favor="+is_favor+"  where goods_id=" + goodsid + " and uid=" + uid)
    return json.dumps({"status": is_favor})


@app.route("/cart/init")
def cartInit():
    id = request.args.get("uid")
    rs=redis.StrictRedis(config.redisConfig["host"],config.redisConfig["port"])
    # rs.flushall()
    msg = rs.hget("cart","u"+str(id))
    if msg ==None:
        rs.hset("cart","u"+str(id),"[]")
    msg = rs.hget("cart", "u" + str(id))
    return json.dumps(json.loads(msg))  #序列化

@app.route("/cart/refresh")
def cartRefresh():
    id = request.args.get("uid")
    data = request.args.get("data")
    rs = redis.StrictRedis(config.redisConfig["host"], config.redisConfig["port"])
    rs.hset("cart","u"+str(id),data)
    return {"status":0}

app.run(host="192.168.1.4", port=4444, debug=True)