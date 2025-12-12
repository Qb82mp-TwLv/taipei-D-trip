from mysql.connector import connect, errors
from dotenv import load_dotenv
import mysql.connector
import os

class connectDB:
    def __init__(self):
        self._cnx = None

    def dbConnecting(self):
        if self._cnx == None or self._cnx.is_connected == False:
            try:
                load_dotenv()
                config = {
                    "host":"127.0.0.1",
                    "user": os.getenv("API_SQL_USER"),
                    "password": os.getenv("API_SQL_PW"),
                    "database": os.getenv("API_SQL_DB")
                }

                self._cnx = mysql.connector.connect(pool_name="conn_Pooling",
                                            pool_size=5,
                                            **config)

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
            if self._cnx == None or self._cnx.is_connected == False:
                self.dbConnecting()
   
            cursor1 = self._cnx.cursor()
            cursor2 = self._cnx.cursor()
            try:
                query_attr = None
                attr_dt= None
                idx = (p*7)+p            
                if CAT != None and keyword != None:
                    # 原本要使用CGROUP_CONCAT()，但群組的字串超過1024字元，若要使用需要修改系統設定。
                    # 修改完還得改回來，但畢竟是系統設定，不想亂動，所以改用子查詢的方式，合併成一條查詢語句。       
                    query_attr = """SELECT img.file, info.* FROM `trip_image` AS img 
                                    INNER JOIN (SELECT cateInfo.* FROM (SELECT * FROM `trip_information` WHERE category=%s) AS cateInfo 
                                    WHERE cateInfo.mrt=%s OR cateInfo.name LIKE %s LIMIT 9 OFFSET %s) AS info ON img.info_id=info.id;"""
                    kw = "%"+keyword+"%"
                    attr_dt = (CAT, keyword, kw, idx)
                elif CAT != None:
                    query_attr = """SELECT img.file, info.* FROM `trip_image` AS img 
                                    INNER JOIN (SELECT * FROM `trip_information` WHERE category=%s LIMIT 9 OFFSET %s) AS info 
                                    ON img.info_id=info.id;"""
                    attr_dt = (CAT, idx)
                elif keyword != None:
                    query_attr = """SELECT img.file, info.* FROM `trip_image` AS img 
                                    INNER JOIN (SELECT * FROM `trip_information` WHERE mrt=%s OR name LIKE %s LIMIT 9 OFFSET %s) AS info
                                    ON img.info_id=info.id;"""
                    kw = "%"+keyword+"%"
                    attr_dt = (keyword, kw, idx)
                else:
                    query_attr = """SELECT img.file, info.* FROM `trip_image` AS img 
                                    INNER JOIN (SELECT * FROM `trip_information` LIMIT 9 OFFSET %s) AS info
                                    ON img.info_id=info.id;"""
                    attr_dt = (idx,)

                cursor1.execute(query_attr, attr_dt)
                findAll = cursor1.fetchall()

                if findAll != []:
                    dtJson = self.attractionFormat(findAll, p)        
                    if dtJson != None:                         
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
        i = -1
        info_id = None
        dt_json = {"nextPage": None, "data":[]}
        for row in dt:
            if info_id != row[1]:
                i +=1
                info_id = row[1]
                if i == 8:
                    pg = p +1
                    dt_json["nextPage"]= pg
                    break

                item = {}
                item["id"] = row[1]
                item["name"] = row[2]
                item["category"] = row[3]
                item["description"] = row[4]
                item["address"] = row[5]
                item["transport"] = row[6]
                item["mrt"] = row[7]
                item["lat"] = row[8]
                item["lng"] = row[9]
                item["images"] = [row[0]]           
                dt_json["data"].append(item)   
            elif "data" in dt_json:
                if "images" in dt_json["data"][i]:
                    dt_json["data"][i]["images"].append(row[0])
            
        return dt_json

            
    async def queryAtrractionId(self, id: int):
        _result = False
        try:
            if self._cnx == None or self._cnx.is_connected == False:
                self.dbConnecting()
            cursor1 = self._cnx.cursor()
            cursor2 = self._cnx.cursor()
            try:
                dt_json = None
                query_id_info = """SELECT img.file, info.* FROM `trip_image`AS img 
                                    INNER JOIN (SELECT * FROM `trip_information` WHERE id=%s) AS info
                                    ON img.info_id=info.id;"""
                cursor1.execute(query_id_info, (id,))
                findAll = cursor1.fetchall()
                if findAll != None:
                    i = 0
                    for row in findAll:
                        if i == 0:
                            dt_json = {"data":{
                                            "id": row[1],
                                            "name": row[2],
                                            "category": row[3],
                                            "description": row[4],
                                            "address": row[5],
                                            "transport": row[6],
                                            "mrt": row[7],
                                            "lat": row[8],
                                            "lng": row[9],
                                            "images": [row[0]]
                                            }}
                            i+=1
                        elif "data" in dt_json:
                            if "images" in dt_json["data"]:
                                dt_json["data"]["images"].append(row[0])
                    
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
            if self._cnx == None or self._cnx.is_connected == False:
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
            if self._cnx == None or self._cnx.is_connected == False:
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