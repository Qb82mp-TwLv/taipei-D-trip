def viewAttractions(data):
	if isinstance(data, dict) and data.get("dt") is not None:
		i = -1
		info_id = None
		dt_json = {"nextPage": None, "data":[]}
		for row in data["dt"]:
			if info_id != row[1]:
				i +=1
				info_id = row[1]
				if i == 8:
					pg = data["page"] +1
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
	else:
		_content = {
			"error": True,
			"message": "請按照情境提供對應的錯誤訊息"
		}
		return _content

def viewAttractionId(data):
	if data != False:
		i = 0
		dt_json = None
		for row in data:
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
		return dt_json
	else:
		_content = {
			"error": True,
			"message": "請按照情境提供對應的錯誤訊息"
		}
		return _content

def viewCAT(data):
	if data != False:
		return {"data": data}
	else:
		_content = {
			"error": True,
			"message": "請按照情境提供對應的錯誤訊息"
		}
		return _content


def viewMRT(data):
	if data != False:
		return {"data": data}
	else:
		_content = {
			"error": True,
			"message": "請按照情境提供對應的錯誤訊息"
		}
		return _content
	
