from dotenv import load_dotenv
from datetime import datetime
import os
import urllib.request
import json
import random

async def payAPIProcess(orderDt):
	try:
		amount = int(orderDt.order.get("price"))
		contactInfo = orderDt.order.get("contact")
		phone = contactInfo.get("phone")
		name = contactInfo.get("name")
		email = contactInfo.get("email")
		
		load_dotenv()
		orderData = {
			"prime": orderDt.prime,
			"partner_key": os.getenv("API_TP_PTNK"),
			"merchant_id": os.getenv("API_TP_MCID"),
			"details": "台北景點一日遊",
			"amount": amount,
			"cardholder": {
				"phone_number": phone,
				"name": name,
				"email": email,
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
		return False
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