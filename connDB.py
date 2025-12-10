from mysql.connector import connect, errors
from dotenv import load_dotenv
import mysql.connector
import os

class connectDB:
    def __init__(self):
        self.is_connected = False
        self._cnx = None

    def dbConnecting(self):
        if self.is_connected != True:
            try:
                load_dotenv()
                config = {
                    "host":"127.0.0.1",
                    "user": "root",
                    "password": os.getenv("API_SQL_PW"),
                    "database": "trip_website"
                }

                self._cnx = mysql.connector.connect(pool_name="conn_Pooling",
                                            pool_size=5,
                                            **config)
                if self._cnx != None:
                    self.is_connected = True

            except errors.ConnectionTimeoutError:
                print("發生超過連線時間錯誤。")
            except errors.PoolError:
                print("使用的連線已超過上限或是連線已關閉。")
            except mysql.connector.Error:
                print("連線異常。")
            except Exception as e:
                print("連線時發生其他錯誤:", e)      


    async def queryAtrractions(self, p: int, CAT: str=None, keyword: str=None):
        _result = False
        try:
            if self.is_connected != True:
                self.dbConnecting()   
            cursor1 = self._cnx.cursor()
            cursor2 = self._cnx.cursor()
            try:
                query_attr = None
                attr_dt= None
                idx = (p*7)+p            
                if CAT != None and keyword != None:
                    # 原本要使用CGROUP_CONCAT()，但群組的字串超過1024字元，若要使用需要修改系統設定。
                    # 修改完還得改回來，但畢竟是系統設定，不想亂動，所以就用兩條連接線處理。
                    query_attr = """SELECT cateInfo.* FROM (SELECT * FROM `trip_information` WHERE category=%s) AS cateInfo 
                                    WHERE cateInfo.mrt=%s OR cateInfo.name LIKE %s LIMIT 9 OFFSET %s;"""       
                    kw = "%"+keyword+"%"
                    attr_dt = (CAT, keyword, kw, idx)
                elif CAT != None:
                    query_attr = """SELECT * FROM `trip_information` 
                                    WHERE category=%s LIMIT 9 OFFSET %s;"""
                    attr_dt = (CAT, idx)
                elif keyword != None:
                    query_attr = """SELECT * FROM `trip_information` 
                                    WHERE mrt=%s OR name LIKE %s LIMIT 9 OFFSET %s;"""
                    kw = "%"+keyword+"%"
                    attr_dt = (keyword, kw, idx)
                else:
                    query_attr = """SELECT * FROM `trip_information` LIMIT 9 OFFSET %s;"""
                    attr_dt = (idx,)

                cursor1.execute(query_attr, attr_dt)
                findAll = cursor1.fetchall()

                if findAll != []:
                    dtJson = self.attractionFormat(findAll, p)        
                    if dtJson != None:
                        i = 0
                        for row in dtJson["data"]:
                            if i == 8:
                                break
                            query_attr_img = """SELECT file FROM `trip_image` WHERE info_id=%s;"""
                            attrImg_dt = (row["id"])
                            cursor2.execute(query_attr_img, (attrImg_dt,))
                            imgFindAll = cursor2.fetchall()
                            if len(imgFindAll) > 0:
                                for file, in imgFindAll:
                                    dtJson["data"][i]["images"].append(file)
                            i += 1
                        
                        _result = dtJson

            except Exception:
                return False
            finally:
                if cursor1 is not None:
                    cursor1.close()
                if cursor2 is not None:
                    cursor2.close()
                
                return _result
        except Exception:
            return False
            

    def attractionFormat(self, dt, p):
        dt_json = None
        if len(dt) == 9:
            pg = p +1
            dt_json = {"nextPage": pg, "data":[]}
        else:
            dt_json = {"nextPage": None, "data":[]}

        i = 0
        for row in dt:
            if i == 8:
                break

            item = {}
            item["id"] = row[0]
            item["name"] = row[1]
            item["category"] = row[2]
            item["description"] = row[3]
            item["address"] = row[4]
            item["transport"] = row[5]
            # if row[6] == None:
            #     item["mrt"] =None
            # else:
            item["mrt"] = row[6]
            item["lat"] = row[7]
            item["lng"] = row[8]
            item["images"] = []
        
            dt_json["data"].append(item)
            i +=1
            
        return dt_json

            
    async def queryAtrractionId(self, id: int):
        _result = False
        try:
            if self.is_connected != True:
                self.dbConnecting()
            cursor1 = self._cnx.cursor()
            cursor2 = self._cnx.cursor()
            try:
                dt_json = None
                query_id_info = """SELECT * FROM `trip_information` WHERE id=%s;"""
                cursor1.execute(query_id_info, (id,))
                findOne = cursor1.fetchone()
                if findOne != None:
                    dt_json = {"data":{
                                    "id": findOne[0],
                                    "name": findOne[1],
                                    "category": findOne[2],
                                    "description": findOne[3],
                                    "address": findOne[4],
                                    "transport": findOne[5],
                                    "mrt": findOne[6],
                                    "lat": findOne[7],
                                    "lng": findOne[8],
                                    "images": []
                                    }}
                    
                    cursor2.execute("""SELECT file FROM `trip_image` WHERE info_id=%s;""", (id,))
                    findImg = cursor2.fetchall()
                    if findImg != []:
                        for file, in findImg:
                            dt_json["data"]["images"].append(file)
                    
                if dt_json != None:
                    _result = dt_json

            except Exception:
                return False
            finally:
                if cursor1 is not None:
                    cursor1.close()
                if cursor2 is not None:
                    cursor2.close()
                    
            return _result
        except Exception:
            return False
        
    async def queryCategory(self):
        _result = False
        try:
            if self.is_connected != True:
                self.dbConnecting()
            cursor = self._cnx.cursor()

            category_dt = []
            cursor.execute("""SELECT category FROM `trip_information` GROUP BY category;""")
            findAll = cursor.fetchall()
            if findAll != []:
                for category, in findAll:
                    category_dt.append(category)
                
            if category_dt != []:
                _result = {"data": category_dt}

            if cursor is not None:
                cursor.close()
            
            return _result
        except Exception:
            return False
        
    async def queryMRT(self):
        _result = False
        try:
            if self.is_connected != True:
                self.dbConnecting()
            cursor = self._cnx.cursor()

            mrt_list = []
            cursor.execute("""SELECT mrt FROM `trip_information` GROUP BY mrt ORDER BY COUNT(mrt) DESC;""")
            findAll = cursor.fetchall()

            if findAll != []:
                for mrt, in findAll:
                    if mrt != None:
                        mrt_list.append(mrt)

            if mrt_list != []:
               _result = {"data": mrt_list} 

            if cursor is not None:
                cursor.close()

            return _result     
        except Exception:
            return False