// 點擊"台北一日遊"的文字，會返回主頁
const homePage = document.querySelector(".Nav-title");
if (homePage){
  homePage.addEventListener("click", function() {
    window.location.href = `/`;
  });
}

getOrderNum();
// 根據收到的訂單編號，確認訂單資訊
async function getOrderNum() {
    const token = localStorage.getItem("token");
    try{
        // http://xxxxxxx:8000/thankyou?number=訂單編號
        const urlStr = new URL(window.location.href);
        // ?number=訂單編號
        // 找出網址中搜尋的參數值
        const urlSearchName = String(urlStr.search);
        const urlSearchNameSplit = urlSearchName.split("=");
        const orderNumber = urlSearchNameSplit[1];
        
        const response = await fetch(`/api/order/${orderNumber}`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        const dt = await response.json();

        if (!response.ok || dt.error !== undefined){
            window.location.href = "/";
        }else{
            if (dt.data === null){
                const contentText = document.querySelector(".content-text");
                contentText.classList.add("text-font");
                contentText.textContent="抱歉，訂單紀錄並未有記錄此筆訂單。";
                const contentInfo = document.querySelector(".content-info");
                contentInfo.className="";
            }else{
                createWeb(dt.data);
            }
        }
    }catch{
        window.location.href = "/";
    }
}

async function createWeb(dt) {
    const contentText = document.querySelector(".content-text");
    if (contentText){
        let textLargeStr = "";

        const newTextMarkTag = document.createElement("div");
        newTextMarkTag.classList.add("text-mark");
        const newTextMarkImgTag = document.createElement("img");
        newTextMarkImgTag.id = "markImg";
        if (dt.status === 0){
            newTextMarkImgTag.src = "/static/img/mark.png";
            textLargeStr = "，感謝您的購買";
        }else{
            newTextMarkImgTag.src = "/static/img/multiply.png";
            textLargeStr = "，抱歉，您的付款失敗";
        }
        newTextMarkTag.appendChild(newTextMarkImgTag);

        const newTextLargeTag = document.createElement("div");
        newTextLargeTag.classList.add("text-large");
        newTextLargeTag.id = "text-title";
        newTextLargeTag.textContent = `${dt.contact.name}${textLargeStr}`;

        const newTextMediumTag = document.createElement("div");
        newTextMediumTag.classList.add("text-medium");
        const newTextMediumTitleTag = document.createElement("div");
        newTextMediumTitleTag.textContent = "訂單編號：";
        const newTextMediumNumberTag = document.createElement("text-number");
        newTextMediumNumberTag.textContent = `${dt.number}`;
        newTextMediumTag.appendChild(newTextMediumTitleTag);
        newTextMediumTag.appendChild(newTextMediumNumberTag);

        const newTextSmallTag = document.createElement("div");
        newTextSmallTag.classList.add("text-samll");
        const newTextSmallStringTag = document.createElement("div");
        newTextSmallStringTag.textContent = "請截圖、拍照或記錄訂單編號，以便日後查詢，謝謝您。";
        newTextSmallTag.appendChild(newTextSmallStringTag);

        contentText.appendChild(newTextMarkTag);
        contentText.appendChild(newTextLargeTag);
        contentText.appendChild(newTextMediumTag);
        contentText.appendChild(newTextSmallTag);
    }

    const contentInfo = document.querySelector(".content-info");
    if(contentInfo){
        const newInfoImgCTNTag = document.createElement("div");
        newInfoImgCTNTag.classList.add("info-img");
        const newInfoImgTag = document.createElement("img");
        newInfoImgTag.src = dt.trip.attraction.image;
        newInfoImgCTNTag.appendChild(newInfoImgTag);

        const newInfoTextTag = document.createElement("div");
        newInfoTextTag.classList.add("info-text");
        const newInfoNameTag = document.createElement("div");
        newInfoNameTag.classList.add("info-name");
        newInfoNameTag.textContent = "景點："+dt.trip.attraction.name;
        const newInfoAddTag = document.createElement("div");
        newInfoAddTag.classList.add("info-address");
        newInfoAddTag.textContent = "地點：" +dt.trip.attraction.address;
        const newInfoDateTag = document.createElement("div");
        newInfoDateTag.classList.add("info-date");
        newInfoDateTag.textContent = "日期：" + dt.trip.date;
        const newInfoTimeTag = document.createElement("div");
        newInfoTimeTag.classList.add("info-time");
        newInfoTimeTag.textContent = "時間：";
        if (dt.trip.time === "afternoon"){
            newInfoTimeTag.textContent += "下午2點到晚上9點";
        }else{
            newInfoTimeTag.textContent += "早上9點到下午4點";
        }
        newInfoTextTag.appendChild(newInfoNameTag);
        newInfoTextTag.appendChild(newInfoAddTag);
        newInfoTextTag.appendChild(newInfoDateTag);
        newInfoTextTag.appendChild(newInfoTimeTag);

        const newInfoPriceTag = document.createElement("div");
        newInfoPriceTag.classList.add("info-price");
        newInfoPriceTag.textContent = "總價：" + String(dt.price);

        contentInfo.appendChild(newInfoImgCTNTag);
        contentInfo.appendChild(newInfoTextTag);
        contentInfo.appendChild(newInfoPriceTag);
    }
}