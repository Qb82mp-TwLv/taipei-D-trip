from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
import jwt
import os
import re

# 會員驗證部分
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


# 傳輸的內容格式驗證
def getSyStemDate():
	# 驗證日期是否已過，前一天還可以訂
	systemTimeUTC = datetime.now(timezone.utc)
	systemTimeTwUTC = systemTimeUTC.astimezone(timezone(timedelta(hours=8)))
	systemDate = systemTimeTwUTC.date()

	return systemDate

def bookVerify(bookDt):
	if bookDt.attractionId > 0:
		# 驗證日期是否已過，前一天還可以訂
		selectD = datetime.strptime(bookDt.date, "%Y-%m-%d").date()
		systemD = getSyStemDate()
		if (selectD > systemD):
			if bookDt.time == "afternoon" or bookDt.time == "morning":
				if int(bookDt.price) == 2000 or int(bookDt.price) == 2500:
					return True
	
	return False

def orderVerify(orderDt):
	trip = orderDt.order["trip"]
	attId = trip["attraction"]["id"]

	# 驗證景點ID
	if isinstance(attId, int) == True and attId > 0:
		# 驗證日期
		selectD = datetime.strptime(str(trip["date"]), "%Y-%m-%d").date()
		systemD = getSyStemDate()

		if (selectD > systemD):
			# 驗證時間
			if str(trip["time"]) == "morning" or str(trip["time"]) == "afternoon":
				amount = int(orderDt.order.get("price"))
				contactInfo = orderDt.order.get("contact")
				phone = contactInfo.get("phone")
				name = contactInfo.get("name")
				email = contactInfo.get("email")
				# 判斷字串長度，與email、手機格式
				emailPattern = r'[A-Za-z][A-Za-z0-9]+([_.][A-Za-z0-9]+)*\@[A-Za-z0-9]+(\.[A-Za-z]+)+'
				if (re.fullmatch(emailPattern, email) and re.fullmatch(r'09[1-9]\d{7}', phone)):
					if (len(str(email)) <= 254) and (len(str(phone)) == 10) and (len(str(name)) <= 60) and (amount == 2000 or amount == 2500):
						return True
	
	return False