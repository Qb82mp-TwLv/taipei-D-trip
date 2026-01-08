// 引用登入功能JS檔案
import { dialogUI } from "../dialog/dialog.js";

// 建立新的預訂行程
const createBookBtn = document.getElementById("startBooking_btn");
if (createBookBtn){
    createBookBtn.addEventListener("click", reservedTrip);
}

async function reservedTrip(){
    const token = localStorage.getItem("token");
    if (token !== null){
        // 取得景點ID
        // http://xxxxxxx:8000/attraction/6
        const urlStr = new URL(window.location.href); 
        // /attraction/6
        const urlPathName = String(urlStr.pathname);
        const urlPathnameSplit = urlPathName.split("/");
        const attId = parseInt(urlPathnameSplit[2], 10);

        const dateStr = document.getElementById("selectDate").value;
        const timeRadioAM = document.getElementById("selectAM");
        const timeRadioPM = document.getElementById("selectPM");
        let timeStr = "";
        // 判斷時間是選擇上午還是下午
        if (timeRadioAM.checked){
            timeStr = "morning";
        }else if(timeRadioPM.checked){
            timeStr = "afternoon";
        }
        const priceStr = document.getElementById("ordPrice").textContent;
        console.log(priceStr);
        const priceStrSplit = priceStr.split(" ");
        const price = parseInt(priceStrSplit[1], 10);

        // 要傳送的預訂資訊
        const bookingInfo = {
            "attractionId": attId,
            "date": dateStr,
            "time": timeStr,
            "price": price
        }

        if (attId && dateStr && timeStr && price){
            // 建立預訂資訊製購物車
            try{
                console.log(1);
                const response = await fetch("/api/booking",{
                    method: "POST",
                    headers: {
                        "Authorization": `Bearer ${token}`,
                        "Content-Type": "application/json"},
                    body: JSON.stringify(bookingInfo)
                });

                const dt = await response.json();
                console.log(2);
                if (!response.ok || dt.error !== undefined){
                    console.log(3);
                    console.log("預訂失敗");
                    alert("行程預訂失敗，請稍後再預訂，謝謝您。");
                }else{
                    window.location.href = "/booking";
                }
            }catch{
                console.log("預訂失敗");
                alert("行程預訂失敗，請稍後再預訂，謝謝您。");
            }
        }else{
            console.log("預訂失敗");
            alert("行程預訂失敗，請稍後再預訂，謝謝您。");
        }
    }else{
        dialogUI.openLoginWindow();
        //console.log("觸發");
    }
}