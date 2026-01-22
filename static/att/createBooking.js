// 引用登入功能JS檔案
import { dialogUI } from "/static/dialog/dialog.js";

// 建立新的預訂行程
const createBookBtn = document.getElementById("startBooking_btn");
if (createBookBtn){
    createBookBtn.addEventListener("click", reservedTrip);
}

async function reservedTrip(){
    const token = localStorage.getItem("token");
    if (token !== null){
        try{
            // 取得景點ID
            // http://xxxxxxx:8000/attraction/6
            const urlStr = new URL(window.location.href); 
            // /attraction/6
            const urlPathName = String(urlStr.pathname);
            const urlPathnameSplit = urlPathName.split("/");
            const attId = parseInt(urlPathnameSplit[2], 10);

            const dateStr = document.getElementById("selectDate").value;
            // 取得當下系統時間
            const sysDate = new Date()
            const month = String(sysDate.getMonth() +1).padStart(2, '0');
            const day = String(sysDate.getDate()).padStart(2, '0'); // 日期為兩位數，若不足兩位數，則補0
            const currentDate = `${sysDate.getFullYear()}-${month}-${day}`;
            
            // 轉為毫秒比對
            const chooseDay = new Date(dateStr);
            const currentDay = new Date(currentDate);
            if (chooseDay > currentDay){
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
                const priceStrSplit = priceStr.split(" ");
                const price = parseInt(priceStrSplit[1], 10);

                // 要傳送的預訂資訊
                const bookingInfo = {
                    "attractionId": attId,
                    "date": dateStr,
                    "time": timeStr,
                    "price": price
                }

                // 只要是空字串、null、undefiined...，就都為false
                if (attId && dateStr && timeStr && price){
                    // 建立預訂資訊製購物車
                    const response = await fetch("/api/booking",{
                        method: "POST",
                        headers: {
                            "Authorization": `Bearer ${token}`,
                            "Content-Type": "application/json"},
                        body: JSON.stringify(bookingInfo)
                    });

                    const dt = await response.json();

                    if (!response.ok || dt.error !== undefined){
                        console.log("預訂失敗");
                        alert("行程預訂失敗，請稍後再預訂，謝謝您。");
                    }else{
                        window.location.href = "/booking";
                    }
                    
                }else{
                    console.log("預訂失敗");
                    alert("行程預訂失敗，請確認該填寫、選擇的資訊都已填寫，謝謝您。");
                }
            }else{
                console.log("預訂失敗");
                alert("行程預訂失敗，請先確認日期是否還未過，並於修改日期後再預訂，謝謝您。");
            }
        }catch{
            console.log("預訂失敗");
            alert("行程預訂失敗，請稍後再預訂，謝謝您。");
        }
    }else{
        dialogUI.openLoginWindow();
    }
}