import pymysql


def doIt(query):
    db = pymysql.Connect("localhost", "root", "root", "mall")
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result

def Excuit(query):
    db = pymysql.Connect("localhost", "root", "root", "mall")
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute(query)
    db.commit()
    cursor.close()
    db.close()
    return 1

#只获取第一条
def getOne(query):
    db = pymysql.Connect("localhost", "root", "root", "mall")
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    db.close()
    return result