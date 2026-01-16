from mysql.connector import connect, errors, OperationalError
from dotenv import load_dotenv
import mysql.connector
import os

class connectDB:
    def __init__(self):
        self._cnx = None

    def dbConnecting(self):
        if self._cnx == None:
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
        elif self._cnx.is_connected == False:
            self._cnx.reconnect(attempts=2, delay=3)

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

                return _result
            except Exception as e:
                print(e)
                return False
            finally:
                if cursor1 is not None:
                    cursor1.close()
                if cursor2 is not None:
                    cursor2.close() 
        except OperationalError:
            self._cnx.reconnect(attempts=2, delay=3)
            return False           
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

                return _result
            except Exception:
                return False
            finally:
                if cursor1 is not None:
                    cursor1.close()
                if cursor2 is not None:
                    cursor2.close()
        except OperationalError:
            self._cnx.reconnect(attempts=2, delay=3)
            return False
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
        except OperationalError:
            self._cnx.reconnect(attempts=2, delay=3)
            return False
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
        except OperationalError:
            self._cnx.reconnect(attempts=2, delay=3)
            return False     
        except Exception:
            return False
        
    async def signInUser(self, userDt):
        _result = False
        try:
            if self._cnx == None or self._cnx.is_connected == False:
                self.dbConnecting()
            cursor = self._cnx.cursor()

            query_user_email = """SELECT email FROM `trip_user` WHERE LOWER(email)=LOWER(%s);"""
            cursor.execute(query_user_email, (userDt.email,))

            findOne = cursor.fetchone()
            if findOne is None:
                _result = {"ok": True}
                create_user = """INSERT INTO `trip_user` (name, email, password)
                                VALUES (%s, %s , %s);"""
                create_dt = (userDt.name, userDt.email, userDt.password)
                cursor.execute(create_user, create_dt)

            if isinstance(_result, dict) and cursor.rowcount == 1:
                self._cnx.commit()
            else:
                self._cnx.rollback()

            return _result
        except OperationalError:
            self._cnx.reconnect(attempts=2, delay=3)
            return False
        except Exception:
            return False



    async def verifyToken(self, userDt):
        _result = False
        try:
            if self._cnx == None or self._cnx.is_connected == False:
                self.dbConnecting()
            cursor = self._cnx.cursor()

            query_user_info = """SELECT _id, name, email FROM `trip_user` WHERE _id=%s AND name=%s AND email=%s;"""
            query_data = (userDt["id"], userDt["name"], userDt["email"])

            cursor.execute(query_user_info, query_data)
            findOne = cursor.fetchone()

            if findOne != None:
                _result = {"data":{
                    "id": findOne[0],
                    "name": findOne[1],
                    "email": findOne[2]
                }}

            if cursor is not None:
                cursor.close()

            return _result
        except OperationalError:
            self._cnx.reconnect(attempts=2, delay=3)
            return False
        except Exception:
            return False


    async def loginUser(self, userDt):
        _result = False
        try:
            if self._cnx == None or self._cnx.is_connected == False:
                self.dbConnecting()
            cursor = self._cnx.cursor()

            query_user_info = """SELECT _id, name, email FROM `trip_user` WHERE LOWER(email)=LOWER(%s) AND password=%s;"""
            query_data = (userDt.email, userDt.password)

            cursor.execute(query_user_info, query_data)
            findOne = cursor.fetchone()

            if findOne is not None:
                _result = {"id": findOne[0], "name": findOne[1], "email": findOne[2]}

            if cursor is not None:
                cursor.close()

            return _result
        except OperationalError:
            self._cnx.reconnect(attempts=2, delay=3)
            return False
        except Exception:
            return False

    async def queryBookATrip(self, userId):
        _result = False
        try:
            if self._cnx == None or self._cnx.is_connected == False:
                self.dbConnecting()
            cursor = self._cnx.cursor()

            query_book_info = """SELECT book.attraction_id, info.name, info.address, img.file, book.book_date, book.book_time, book.price 
                                FROM `trip_booking`AS book 
                                INNER JOIN `trip_information` AS info ON info.id=book.attraction_id
                                INNER JOIN `trip_image` AS img ON info.id=img.info_id AND member_id=%s;"""
            cursor.execute(query_book_info, (userId,))

            findAll = cursor.fetchall()
            if len(findAll) > 0:
                dateStr = findAll[0][4].strftime("%Y-%m-%d")

                _result={
                    "data":{
                        "attraction": {
                            "id": findAll[0][0],
                            "name": findAll[0][1],
                            "address": findAll[0][2],
                            "image": findAll[0][3]
                        },
                        "date": dateStr,
                        "time": findAll[0][5],
                        "price": findAll[0][6]
                    }
                }

            if cursor is not None:
                cursor.close()

            return _result
        except OperationalError:
            self._cnx.reconnect(attempts=2, delay=3)
            return False
        except Exception:
            return False


    async def createBookATrip(self, bookingDt, userId):
        _result = False
        try:
            if self._cnx == None or self._cnx.is_connected == False:
                self.dbConnecting()
            cursor = self._cnx.cursor()

            create_booking_info = """INSERT INTO `trip_booking` (attraction_id, member_id, book_date, book_time, price) 
                                    VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY 
                                    UPDATE `attraction_id`=%s, `book_date`=%s, `book_time`=%s, `price`=%s;"""
            create_data = (bookingDt.attractionId, userId, bookingDt.date, bookingDt.time, bookingDt.price, bookingDt.attractionId, bookingDt.date, bookingDt.time, bookingDt.price)

            cursor.execute(create_booking_info, create_data)
            if cursor.rowcount > 0:
                _result = {"ok": True}
                self._cnx.commit()
            else:
                self._cnx.rollback()

            if cursor is not None:
                cursor.close()

            return _result
        except OperationalError:
            self._cnx.reconnect(attempts=2, delay=3)
            return False
        except Exception:
            return False
        

    async def delBookATrip(self, userId):
        _result = False
        try:
            if self._cnx == None or self._cnx.is_connected == False:
                self.dbConnecting()
            cursor = self._cnx.cursor()

            del_booking_info = """DELETE FROM `trip_booking` WHERE member_id=%s;"""
            cursor.execute(del_booking_info, (userId,))

            if cursor.rowcount == 1:
                self._cnx.commit()
                _result = {"ok": True}
            else:
                self._cnx.rollback()

            if cursor is not None:
                cursor.close()

            return _result
        except OperationalError:
            self._cnx.reconnect(attempts=2, delay=3)
            return False
        except Exception:
            return False
        
    async def createOrderInfo(self, ordInfo, ordNum, userId):
        _result = False
        try:
            if self._cnx == None or self._cnx.is_connected == False:
                self.dbConnecting()
            cursor = self._cnx.cursor()

            create_order_info = """INSERT INTO `trip_order` (order_number, att_id, book_date, book_time, price, member_id, phone, pay_status)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""
            
            att_id = ordInfo.order["trip"]["attraction"]["id"]
            book_date = ordInfo.order["trip"]["date"]
            book_time = ordInfo.order["trip"]["time"]
            price = ordInfo.order["price"]
            phone=ordInfo.order["contact"]["phone"]
            create_data = (ordNum, att_id, book_date, book_time, price, userId, phone, "UNPAID")

            cursor.execute(create_order_info, create_data)
            if cursor.rowcount == 1:
                self._cnx.commit()
                _result = True
            else:
                self._cnx.rollback()

            if cursor is not None:
                cursor.close()

            return _result
        except OperationalError:
            self._cnx.reconnect(attempts=2, delay=3)
            return False
        except Exception:
            return False
        
    async def orderPayStatus(self, ordNum, userId):
        try: 
            if self._cnx == None or self._cnx.is_connected == False:
                self.dbConnecting()
            cursor = self._cnx.cursor()

            upd_order_info = """UPDATE `trip_order`
                                SET pay_status='PAID'
                                WHERE order_number=%s AND member_id=%s;"""
            upd_data = (ordNum, userId)

            cursor.execute(upd_order_info, upd_data)
            if cursor.rowcount == 1:
                self._cnx.commit()
            else:
                self._cnx.rollback()

            if cursor is not None:
                cursor.close()
        except OperationalError:
            self._cnx.reconnect(attempts=2, delay=3)
        except Exception as e:
            print(e)
         
    
    async def createPayInfo(self, ordNum, payId, userId, status):
        _result = False
        try:
            if self._cnx == None or self._cnx.is_connected == False:
                self.dbConnecting()
            cursor = self._cnx.cursor()

            creat_pay_info = """INSERT INTO `trip_pay` (order_number, payment_id, status, member_id)
                                VALUES (%s, %s, %s, %s);"""     
            create_data = (ordNum, payId, status, userId)

            cursor.execute(creat_pay_info, create_data)
            if cursor.rowcount == 1:
                self._cnx.commit()
                _result = True
            else:
                self._cnx.rollback()

            if cursor is not None:
                cursor.close()

            return _result
        except OperationalError:
            self._cnx.reconnect(attempts=2, delay=3)
            return False
        except Exception:
            return False
        

    async def queryOrderInfo(self, ordNum, user):
        _result = False
        try:
            if self._cnx == None or self._cnx.is_connected == False:
                self.dbConnecting()
            cursor = self._cnx.cursor()

            query_ord_info = """SELECT * FROM (SELECT ord.order_number AS ordNum, ord.att_id, info.name, info.address, img.file, ord.book_date, ord.book_time, ord.price, ord.pay_status, ord.phone 
                                FROM `trip_order`AS ord 
                                INNER JOIN `trip_information` AS info ON info.id=ord.att_id
                                INNER JOIN `trip_image` AS img ON info.id=img.info_id AND ord.member_id=%s) AS membOrd WHERE membOrd.ordNum=%s;"""
            query_data = (user["id"], ordNum)
           
            cursor.execute(query_ord_info, query_data)
            findAll = cursor.fetchall()
 
            if findAll != []:
                payStatus = 1               
                if findAll[0][8] == "PAID":
                    payStatus = 0

                _result = {
                    "data": {
                        "number": ordNum,
                        "price": findAll[0][7],
                        "trip": {
                            "attraction": {
                                "id": findAll[0][1],
                                "name": findAll[0][2],
                                "address": findAll[0][3],
                                "image": findAll[0][4]
                            },
                            "date": findAll[0][5],
                            "time": findAll[0][6]
                        },
                        "contact": {
                            "name": user["name"],
                            "email": user["email"],
                            "phone": findAll[0][9]
                        },
                        "status": payStatus
                    }
                }
            
            if cursor is not None:
                cursor.close()
            
            return _result
        except OperationalError:
            self._cnx.reconnect(attempts=2, delay=3)
            return False
        except Exception:
            return False
