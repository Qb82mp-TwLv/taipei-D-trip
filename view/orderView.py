def viewCreateOrder(data,  ordNum):
    if data["status"] == "Success":
        _payStatus = {
            "status": 0,
            "message": "付款成功"
        }
    else:
        _payStatus = {
            "status": 1,
            "message": "付款失敗"
        }
    _result = {
        "data": {
            "number": ordNum,
            "payment": _payStatus
        }
    }

    return _result


def viewGetOrderInfo(data, ordNum, user):
    if data != False:
        payStatus = 1               
        if data[0][8] == "PAID":
            payStatus = 0

        dt_json = {
            "data": {
                "number": ordNum,
                "price": data[0][7],
                "trip": {
                    "attraction": {
                        "id": data[0][1],
                        "name": data[0][2],
                        "address": data[0][3],
                        "image": data[0][4]
                    },
                    "date": data[0][5],
                    "time": data[0][6]
                },
                "contact": {
                    "name": user["name"],
                    "email": user["email"],
                    "phone": data[0][9]
                },
                "status": payStatus
            }
        }
        return dt_json
    else:
        return False