from fastapi import *
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from connDB import connectDB
from dotenv import load_dotenv
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
import jwt
import os
import urllib.request
import json
import random
from async_lru import alru_cache



app=FastAPI()
getdt = connectDB()

app.mount("/static", StaticFiles(directory="static"), name="static")
# 取得request的Authenticate Bearer的token參數
# 使用auto_error=False的話，若沒找到權杖，只會回傳None
oauth2_getBearer = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
	return FileResponse("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
	return FileResponse("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
	return FileResponse("./static/thankyou.html", media_type="text/html")


@app.get("/api/attractions")
async def getAttractionInfoList(page: int, category: str=None, keyword: str=None):
	_content = {
		"error": True,
		"message": "請按照情境提供對應的錯誤訊息"
	}

	_result = await getdt.queryAtrractions(page, category, keyword)
	if isinstance(_result, dict) and _result.get("data") is not None:
		return JSONResponse(_result)
	else:
		return JSONResponse(_content)

@alru_cache(maxsize=100)
async def getAttId(attractionId):
	_attIdInfo= await getdt.queryAtrractionId(attractionId)
	return _attIdInfo

@app.get("/api/attraction/{attractionId}")
async def getAttractionIdInfo(attractionId: int):
	_content = {
		"error": True,
		"message": "請按照情境提供對應的錯誤訊息"
	}
	_result = await getAttId(attractionId)
	if isinstance(_result, dict) and _result.get("data") is not None:
		return JSONResponse(_result)
	else:
		return JSONResponse(_content)

@alru_cache(maxsize=1)
async def getCAT():
	_CATDt = await getdt.queryCategory()
	return _CATDt
		
@app.get("/api/categories")
async def getCategoriesList():
	_content = {
		"error": True,
		"message": "請按照情境提供對應的錯誤訊息"
	}
	_result = await getCAT()
	if isinstance(_result, dict) and _result.get("data") is not None:
		return JSONResponse(_result)
	else:
		return JSONResponse(_content)

@alru_cache(maxsize=1)
async def getMRT():
	_mrtDt = await getdt.queryMRT()
	return _mrtDt

@app.get("/api/mrts")
async def getMRTList():
	_content = {
		"error": True,
		"message": "請按照情境提供對應的錯誤訊息"
	}
	_result = await getMRT()
	if isinstance(_result, dict) and _result.get("data") is not None:
		return JSONResponse(_result)
	else:
		return JSONResponse(_content)

# 接收json的資料		
class signInInfo(BaseModel):
	name: str
	email: str
	password: str

@app.post("/api/user")
async def signIn(userDt: signInInfo):
	_content = {
		"error": True,
		"message": "請按照情境提供對應的錯誤訊息"
	}
	_result = await getdt.signInUser(userDt)

	if isinstance(_result, dict) and _result.get("ok") is not None:
		return JSONResponse(_result)
	else:
		return JSONResponse(_content)

@app.get("/api/user/auth")
async def getCurrentUser(token: Optional[str]=Depends(oauth2_getBearer)):  # 使用Depends的方式呼叫取token的方法，並接收回傳的值
	if token != None:
		dtJson = decodeToken(token)
		if isinstance(dtJson, dict):
			_result = await getdt.verifyToken(dtJson)
			if isinstance(_result, dict):
				return JSONResponse(_result)
			else:
				return JSONResponse({"data": None})
		else:
			return JSONResponse({"data": None})
	
	return JSONResponse({"data": None})


class loginInfo(BaseModel):
	email: str
	password: str

@app.put("/api/user/auth")
async def login(userDt: loginInfo):
	_content = {
		"error": True,
		"message": "請按照情境提供對應的錯誤訊息"
	}

	_result = await getdt.loginUser(userDt)
	if isinstance(_result, dict) and _result.get("email") is not None:
		try:
			_tokenEncoded = encodeToken(_result)
			if isinstance(_tokenEncoded, bool):
				return JSONResponse(_content)
			else:
				_token = {"token": _tokenEncoded}
			return JSONResponse(_token)
		except Exception:
			return JSONResponse(_content)
	else:
		return JSONResponse(_content)


def encodeToken(userData):
	encodedData = False
	if isinstance(userData, dict):
		load_dotenv()
		_addSalt = os.getenv("API_TK_K")

		# 將時間使用UTC的格式計算，避免跨時區的問題，確保一致性(標準)
		expiryDate = datetime.now(timezone.utc) + timedelta(days=7)
		# jwt的exp需要使用秒數的整數進行儲存
		userData["exp"] = int(expiryDate.timestamp())

		encodedData = jwt.encode(userData, _addSalt, algorithm="HS256")
	return encodedData


def decodeToken(token):
	load_dotenv()
	_addSalt = os.getenv("API_TK_K")
	
	try:
		userDataJson = jwt.decode(token, _addSalt, algorithms=["HS256"])
		
		return userDataJson
	except ExpiredSignatureError:
		print("效期已過")
		return False
	except InvalidTokenError:
		return False
	except Exception:
		return False
	

@app.get("/api/booking")
async def getShoppingCartInfo(token: Optional[str]=Depends(oauth2_getBearer)):
	_content = {
		"error": True,
		"message": "請按照情境提供對應的錯誤訊息"
	}

	if token != None:
		try:
			dtJson = decodeToken(token)
			if isinstance(dtJson, dict):
				_verify = await getdt.verifyToken(dtJson)
				if _verify.get("data") != None:
					userId = _verify["data"]["id"]
					_result = await getdt.queryBookATrip(userId)
					if _result.get("data").get("attraction") != None:
						return JSONResponse(_result)
			
			return JSONResponse({"data": None})
		except Exception:
			return JSONResponse({"data": None})
	else:
		return JSONResponse(_content)


class bookInfo(BaseModel):
	attractionId: int
	date: str
	time: str
	price: int

@app.post("/api/booking")
async def createShoppingCartInfo(bookDt: bookInfo, token: Optional[str]=Depends(oauth2_getBearer)):
	_content = {
		"error": True,
		"message": "請按照情境提供對應的錯誤訊息"
	}
	
	if token != None:
		try:
			dtJson = decodeToken(token)
			if isinstance(dtJson, dict):
				_verify = await getdt.verifyToken(dtJson)
				if _verify.get("data") != None:
					userId = _verify["data"]["id"]
					_result = await getdt.createBookATrip(bookDt, userId)
					if _result.get("ok") != None:
						return JSONResponse(_result)
				
			return JSONResponse(_content)
		except Exception:
			# 內部發生錯誤
			return JSONResponse(_content)
	else:
		# 當未登入的狀態，拒絕存取
		return JSONResponse(_content)


@app.delete("/api/booking")	
async def deleteShoppingCartInfo(token: Optional[str]=Depends(oauth2_getBearer)):
	_content = {
		"error": True,
		"message": "請按照情境提供對應的錯誤訊息"
	}

	if token != None:
		try:
			dtJson = decodeToken(token)
			if isinstance(dtJson, dict):
				_verify = await getdt.verifyToken(dtJson)
				if _verify.get("data") != None:
					userId = _verify["data"]["id"]
					_result = await getdt.delBookATrip(userId)
					if _result.get("ok") != None:
						return JSONResponse(_result)

			return JSONResponse(_content)
		except Exception:
			return JSONResponse(_content)
	else:
		return JSONResponse(_content)


@app.get("/api/sdk")
async def getSDKVal(token: Optional[str]=Depends(oauth2_getBearer)):
	_content = {
		"error": True,
		"message": "請按照情境提供對應的錯誤訊息"
	}

	if token != None:
		# 確認有登入且是會員
		dtJson =decodeToken(token)
		if isinstance(dtJson, dict):
			load_dotenv()
			_num = os.getenv("API_TP_D")
			_ap = os.getenv("API_TP_K")

			if (_num != "" and _ap != ""):
				return {"one":_num, "two": _ap}
		
		return JSONResponse(_content)
	else:
		return JSONResponse(_content)


class orderInfo(BaseModel):
	prime: str
	order: dict

@app.post("/api/orders")
async def createOrder(orderDt: orderInfo, token: Optional[str]=Depends(oauth2_getBearer)):
	_content = {
		"error": True,
		"message": "請按照情境提供對應的錯誤訊息"
	}

	if token != None:
		try:
			dtJson = decodeToken(token)
			if isinstance(dtJson, dict):
				# # 產生訂單編號
				ordNum = orderNumber(orderDt.order["trip"]["attraction"]["id"])

				# 紀錄訂單的資訊
				_orderREC = await getdt.createOrderInfo(orderDt, ordNum, dtJson["id"])
				if _orderREC == True:
					# 確認付款資訊
					_payResult = await payAPIProcess(orderDt)

					if _payResult != False:
						if _payResult["status"] == "Success":
							_payStatus = {
								"status": 0,
								"message": "付款成功"
							}
							# 修改訂單的付款狀態
							await getdt.orderPayStatus(ordNum, dtJson["id"])
						else:
							_payStatus = {"status": 1,
											"message": "付款失敗"}
						_result = {
							"data": {
								"number": ordNum,
								"payment": _payStatus
							}
						}

						# 紀錄付款資訊
						_createPay = await getdt.createPayInfo(ordNum, _payResult["payId"], dtJson["id"], _payResult["status"])

						# 移除預定的資料
						_delResult = await getdt.delBookATrip(dtJson["id"])

						# 回傳付款結果
						return JSONResponse(_result)								
			return JSONResponse(_content)
		except Exception:
			# 內部發生錯誤
			return JSONResponse(_content)
	else:
		# 當未登入的狀態，拒絕存取
		return JSONResponse(_content)
	

async def payAPIProcess(orderDt):
	try:
		load_dotenv()
		orderData = {
			"prime": orderDt.prime,
			"partner_key": os.getenv("API_TP_PTNK"),
			"merchant_id": os.getenv("API_TP_MCID"),
			"details": "台北景點一日遊",
			"amount": orderDt.order["price"],
			"cardholder": {
				"phone_number": orderDt.order["contact"]["phone"],
				"name": orderDt.order["contact"]["name"],
				"email": orderDt.order["contact"]["email"],
			},
			"remember": False
		}			

		encodedDt= json.dumps(orderData).encode('utf-8')
		payRequest = urllib.request.Request(
			"https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime",
			data= encodedDt,
			headers={
				'Content-Type': 'application/json',
				'x-api-key': os.getenv("API_TP_PTNK")
			}
		)
						
		with urllib.request.urlopen(payRequest) as response:
			info = response.read().decode('utf-8')
			infoDict = json.loads(info)
			payId = str(infoDict["rec_trade_id"])

			# 取status
			if (infoDict["status"] == 0 and infoDict["msg"] == "Success"):
				result = {
					"status":"Success", 
					"payId": payId
				}
			else:
				result = {
					"status":"Fail", 
					"payId": payId
				}

			return result
	except Exception:
		return False

def orderNumber(att_id):
	dateNow = datetime.now()
	# 取年月日小時分鐘秒
	dateStr = dateNow.strftime("%Y%m%d%H%M%S")
	# 隨機亂數
	randomStr = str(random.randint(1000000000,9999999999))
	# 訂單編號
	if len(str(att_id)) == 1:
		id = "0"+str(att_id)
		orderNum = dateStr+randomStr+id
	else:
		orderNum = dateStr+randomStr+str(att_id)
	return orderNum

@app.get("/api/order/{orderNumber}")
async def getOrderInfo(orderNumber: str, token: Optional[str]=Depends(oauth2_getBearer)):
	_content = {
		"error": True,
		"message": "請按照情境提供對應的錯誤訊息"
	}

	if (token != None):
		try:
			# 確認為會員的驗證
			dtJson = decodeToken(token)
			if isinstance(dtJson, dict):
				_result = await getdt.queryOrderInfo(orderNumber, dtJson)
				if isinstance(_result, dict):
					return JSONResponse(_result)
			
			return JSONResponse({"data": None})
		except:
			return JSONResponse({"data": None})
	else:
		return JSONResponse(_content)