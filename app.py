from fastapi import *
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from connDB import connectDB
from dotenv import load_dotenv
from pydantic import BaseModel
from async_lru import alru_cache
from model.validation import decodeToken, bookVerify, orderVerify
from model.paymentProcessing import payAPIProcess, orderNumber
from view.attInfoView import viewMRT, viewCAT, viewAttractionId, viewAttractions
from view.userView import viewSign, viewCurrentUser, viewLogin
from view.bookingView import viewGetShopCarInfo
from view.orderView import viewCreateOrder, viewGetOrderInfo
import os
import re



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
	_result = await getdt.queryAtrractions(page, category, keyword)
	viewContent = viewAttractions(_result)
	return JSONResponse(viewContent)


@alru_cache(maxsize=100)
async def getAttId(attractionId):
	_attIdInfo= await getdt.queryAtrractionId(attractionId)
	return _attIdInfo

@app.get("/api/attraction/{attractionId}")
async def getAttractionIdInfo(attractionId: int):
	_result = await getAttId(attractionId)
	viewContent = viewAttractionId(_result)
	return JSONResponse(viewContent)


@alru_cache(maxsize=1)
async def getCAT():
	_CATDt = await getdt.queryCategory()
	return _CATDt
		
@app.get("/api/categories")
async def getCategoriesList():
	_result = await getCAT()
	viewContent = viewCAT(_result)
	return JSONResponse(viewContent)


@alru_cache(maxsize=1)
async def getMRT():
	_mrtDt = await getdt.queryMRT()
	return _mrtDt

@app.get("/api/mrts")
async def getMRTList():
	_result = await getMRT()
	viewConent = viewMRT(_result)
	return JSONResponse(viewConent)
	

# 接收json的資料		
class signInInfo(BaseModel):
	name: str
	email: str
	password: str

@app.post("/api/user")
async def signIn(userDt: signInInfo):
	# 驗證email格式，判斷名字與密碼長度
	emailPattern = r'[A-Za-z][A-Za-z0-9]+([_.][A-Za-z0-9]+)*\@[A-Za-z0-9]+(\.[A-Za-z]+)+'
	if re.fullmatch(emailPattern, userDt.email) and (len(userDt.email) < 254) and (len(userDt.name) < 60) and (len(userDt.password) < 100):
		_result = await getdt.signInUser(userDt)
		viewContent = viewSign(_result)
		return JSONResponse(viewContent)

	return JSONResponse({"error": True, "message": "請按照情境提供對應的錯誤訊息"})


@app.get("/api/user/auth")
async def getCurrentUser(token: Optional[str]=Depends(oauth2_getBearer)):  # 使用Depends的方式呼叫取token的方法，並接收回傳的值
	if token != None:
		dtJson = decodeToken(token)
		if isinstance(dtJson, dict):
			_result = await getdt.verifyToken(dtJson)
			viewContent = viewCurrentUser(_result)
			return JSONResponse(viewContent)
			
	return JSONResponse({"data": None})


class loginInfo(BaseModel):
	email: str
	password: str

@app.put("/api/user/auth")
async def login(userDt: loginInfo):
	emailPattern = r'[A-Za-z][A-Za-z0-9]+([_.][A-Za-z0-9]+)*\@[A-Za-z0-9]+(\.[A-Za-z]+)+'
	if re.fullmatch(emailPattern, userDt.email) and (len(userDt.email) < 254) and (len(userDt.password) < 100):
		_result = await getdt.loginUser(userDt)
		viewConent = viewLogin(_result)
		return JSONResponse(viewConent)
		
	return JSONResponse({"error": True,	"message": "請按照情境提供對應的錯誤訊息"})


@app.get("/api/booking")
async def getShoppingCartInfo(token: Optional[str]=Depends(oauth2_getBearer)):
	if token != None:
		try:
			dtJson = decodeToken(token)
			if isinstance(dtJson, dict):
				_verify = await getdt.verifyToken(dtJson)
				userInfo = viewCurrentUser(_verify)
				if userInfo.get("data") != None:
					userId = userInfo["data"]["id"]
					_result = await getdt.queryBookATrip(userId)
					viewContent = viewGetShopCarInfo(_result)
					if isinstance(viewContent, dict):
						return JSONResponse(viewContent)
			
			return JSONResponse({"data": None})
		except Exception:
			return JSONResponse({"data": None})
	else:
		return JSONResponse({"error": True,	"message": "請按照情境提供對應的錯誤訊息"})


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
			# 驗證傳輸過來的資料
			if bookVerify(bookDt) == True:
				dtJson = decodeToken(token)
				if isinstance(dtJson, dict):
					_verify = await getdt.verifyToken(dtJson)
					userInfo = viewCurrentUser(_verify)
					if userInfo.get("data") != None:
						userId = userInfo["data"]["id"]
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
				userInfo = viewCurrentUser(_verify)
				if userInfo.get("data") != None:
					userId = userInfo["data"]["id"]
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
				# 驗證
				if orderVerify(orderDt) == True:

					# # 產生訂單編號
					ordNum = orderNumber(orderDt.order["trip"]["attraction"]["id"])

					# 紀錄訂單的資訊
					_orderREC = await getdt.createOrderInfo(orderDt, ordNum, dtJson["id"])
					if _orderREC == True:
						# 確認付款資訊
						_payResult = await payAPIProcess(orderDt)

						if _payResult != False:
							viewContent = viewCreateOrder(_payResult, ordNum)
							if viewContent["data"]["payment"]["status"] == 0:
								# 修改訂單的付款狀態
								await getdt.orderPayStatus(ordNum, dtJson["id"])
							
							# 紀錄付款資訊
							_createPay = await getdt.createPayInfo(ordNum, _payResult["payId"], dtJson["id"], _payResult["status"])

							# 移除預定的資料
							_delResult = await getdt.delBookATrip(dtJson["id"])

							# 回傳付款結果
							return JSONResponse(viewContent)
												
			return JSONResponse(_content)
		except Exception:
			# 內部發生錯誤
			return JSONResponse(_content)
	else:
		# 當未登入的狀態，拒絕存取
		return JSONResponse(_content)


@app.get("/api/order/{orderNumber}")
async def getOrderInfo(orderNumber: str, token: Optional[str]=Depends(oauth2_getBearer)):
	if (token != None):
		# 檢查是否都數字，且長度等於26個
		if (orderNumber.isdigit() == True) and len(orderNumber) == 26:
			try:
				# 確認為會員的驗證
				dtJson = decodeToken(token)
				if isinstance(dtJson, dict):
					_result = await getdt.queryOrderInfo(orderNumber, dtJson)
					viewContent = viewGetOrderInfo(_result, orderNumber, dtJson)
					if isinstance(viewContent, dict):
						return JSONResponse(viewContent)
				
				return JSONResponse({"data": None})
			except:
				return JSONResponse({"data": None})
		return JSONResponse({"data": None})
	else:
		return JSONResponse({"error": True,	"message": "請按照情境提供對應的錯誤訊息"})