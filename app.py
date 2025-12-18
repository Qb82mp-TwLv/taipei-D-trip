from fastapi import *
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from connDB import connectDB

app=FastAPI()
getdt = connectDB()

app.mount("/static", StaticFiles(directory="static"), name="static")


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
		