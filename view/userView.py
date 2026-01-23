from model.validation import encodeToken

def viewSign(data):
	if data != False:
		return {"ok": True}
	else:
		_content = {
            "error": True,
            "message": "請按照情境提供對應的錯誤訊息"
        }
		return _content
	

def viewCurrentUser(data):
	if data != False:
		dt_json = {
			"data":{
				"id": data[0],
				"name": data[1],
				"email": data[2]
        	}
		}
		return dt_json
	else:
		return {"data": None}
	

def viewLogin(data):
	_content = {
		"error": True,
		"message": "請按照情境提供對應的錯誤訊息"
	}

	if data != False:
		try:
			dt_json = {"id": data[0], "name": data[1], "email": data[2]}
			_tokenEncoded = encodeToken(dt_json)
			if isinstance(_tokenEncoded, bool):
				return _content
			else:
				_token = {"token": _tokenEncoded}
			return _token
		except Exception:
			return _content
	else:
		return _content