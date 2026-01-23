def viewGetShopCarInfo(data):
    if data != False:
        dateStr = data[0][4].strftime("%Y-%m-%d")

        dt_json={
            "data":{
                "attraction": {
                    "id": data[0][0],
                    "name": data[0][1],
                    "address": data[0][2],
                    "image": data[0][3]
                },
                "date": dateStr,
                "time": data[0][5],
                "price": data[0][6]
            }
        }
        return dt_json
    else:
        return False