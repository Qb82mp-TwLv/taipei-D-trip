from mysql.connector import errorcode
from dotenv import load_dotenv
import mysql.connector
import json
import os



class connectDB:
    def __init__(self):
        load_dotenv()
        self.connDB = None
        try:
            config = {
                "user": "root",
                "password": os.getenv("API_SQL_PW"),
                "database": "trip_website"
                }

            self.connDB = mysql.connector.connect(**config)
        except errorcode.ER_ACCESS_DENIED_ERROR:
            print("帳號或密碼錯誤。")
        except errorcode.ER_BAD_DB_ERROR:
            print("資料庫不存在。")

    def insertDtInfor(self):
        if self.connDB != None:
            dtDict = None
            # 讀取json格式           
            with open('../taipei-day-trip/data/taipei-attractions.json', 'r', encoding='utf-8') as f:
                jsonfile = f.read()
                jsonToDict = json.loads(jsonfile)
                dtDict = jsonToDict["result"]["results"]

            if isinstance(jsonToDict, dict):
                cursor = self.connDB.cursor()
                cursor2 = self.connDB.cursor()
                try:
                    self.info_result = None
                    for dt in dtDict:
                        add_info ="""INSERT INTO `trip_information`(id, name, category, description, address, transport, mrt,
                                    latitude, longitude) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"""
                        info_name = dt['name'].replace(" ", "")
                        info_CAT = dt['CAT'].replace(" ", "")
                        info_desc = dt['description'].replace(" ", "")
                        info_address = dt['address'].replace(" ", "")
                        info_direc = dt['direction'].replace(" ", "")
                        info_MRT = None
                        if dt['MRT'] != None:
                            info_MRT = dt['MRT'].replace(" ", "")
                        info_dt = (dt['_id'], info_name, info_CAT, info_desc, info_address,
                                   info_direc, info_MRT, dt['latitude'], dt['longitude'])
                        
                        cursor.execute(add_info, info_dt)
                        writeSuccessRow = cursor.rowcount
                        if writeSuccessRow == 1:
                            self.connDB.commit()
                        else:
                            # 將為提交的變更做撤銷
                            self.connDB.rollback()


                        imgStr = dt['file']
                        strSplit = imgStr.split("https")
                        for imgUrl in strSplit:
                            if ".jpg" in imgUrl or ".JPG" in imgUrl or ".png" in imgUrl or ".PNG" in imgUrl:    
                                add_img = """INSERT INTO `trip_image`(info_id, file) VALUES (%s, %s);"""
                                
                                imgUrlStr = "https"+imgUrl.replace(" ", "")
                                img_dt = (dt['_id'], imgUrlStr)
                                
                                cursor2.execute(add_img, img_dt)
                                writeImgSuccessRow = cursor2.rowcount
                                if writeImgSuccessRow == 1:
                                    self.connDB.commit()
                                else:
                                    self.connDB.rollback()
                except Exception as e:
                    self.connDB.rollback()
                    print("發生錯誤:", e)
                finally:
                    if cursor is not None: 
                        cursor.close()
                    if cursor2 is not None:
                        cursor2.close()
                    if self.connDB is not None:
                        self.connDB.close()             
        else:
            print("資料庫沒有連線。")        


if __name__ == "__main__":
    connDB = connectDB()
    connDB.insertDtInfor()       
