from fastapi import *
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from connDB import connectDB
from dotenv import load_dotenv
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
import jwt
import os


app=FastAPI()
getdt = connectDB()

app.mount("/static", StaticFiles(directory="static"), name="static")
# 取得request的Authenticate Bearer的token參數
oauth2_getBearer = OAuth2PasswordBearer(tokenUrl="token")

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


@app.get("/api/attraction/{attractionId}")
async def getAttractionIdInfo(attractionId: int):
	_content = {
		"error": True,
		"message": "請按照情境提供對應的錯誤訊息"
	}
	_result = await getdt.queryAtrractionId(attractionId)
	if isinstance(_result, dict) and _result.get("data") is not None:
		return JSONResponse(_result)
	else:
		return JSONResponse(_content)

		
@app.get("/api/categories")
async def getCategoriesList():
	_content = {
		"error": True,
		"message": "請按照情境提供對應的錯誤訊息"
	}
	_result = await getdt.queryCategory()
	if isinstance(_result, dict) and _result.get("data") is not None:
		return JSONResponse(_result)
	else:
		return JSONResponse(_content)
	

@app.get("/api/mrts")
async def getMRTList():
	_content = {
		"error": True,
		"message": "請按照情境提供對應的錯誤訊息"
	}
	_result = await getdt.queryMRT()
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
async def getCurrentUser(token: Annotated[str, Depends(oauth2_getBearer)]):  # 使用Depends的方式呼叫取token的方法，並接收回傳的值
	dtJson = decodeToken(token)
	if isinstance(dtJson, dict):
		_result = await getdt.verifyToken(dtJson)
		if isinstance(_result, dict):
			return JSONResponse(_result)
		else:
			return JSONResponse({"data": None})
	else:
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
		except Exception as e:
			print(e)
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