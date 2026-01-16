async function initSetting() {
    const token = localStorage.getItem("token");
    const response = await fetch("/api/sdk", {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    const dt = await response.json();
    if (response.ok && dt.one !== undefined){
        let num = parseInt(dt.one, 10);
        TPDirect.setupSDK(num, dt.two, 'sandbox');
        delete dt.one;
        delete dt.two;
        num = 0;
    }
}
initSetting();

async function buildPayProcaess(){
    TPDirect.card.setup({
        fields: {
            number:{
                element: "#card-Num",
                placeholder: '**** **** **** ****'
            },
            expirationDate: {
                element: document.getElementById("card-exp-date"),
                placeholder: 'MM / YY'
            },
            ccv: {
                element: "#card-cvv",
                placeholder: 'CVV'
            }
        },
        styles: {
            'input': {
                'color': 'gray'
            },
            'input.card-number': {
                'font-size': '16px',
                'font-weight': '500',
                'font-family': 'Noto Sans TC',
            },
            'input.expiration-date': {
                'font-size': '16px',
                'font-weight': '500',
                'font-family': 'Noto Sans TC',
            },
            'input.ccv': {
                'font-size': '16px',
                'font-weight': '500',
                'font-family': 'Noto Sans TC',
            },
            ':focus': {
                'color': 'blcak'
            },
            '.valid': {
                'color': 'green'
            },
            '.invalid': {
                'color': 'red'
            },
            '@media screen and (max-width: 400px)': {
                'input': {
                    'color': 'orange'
                }
            }
        },
    });
};


async function getPrimeFromTPD() {
    try{
        TPDirect.card.getPrime((result) => {
            if (result.status !== 0){
                alert("現在無法購買，請稍後再到此頁面購買，謝謝您。");
                return;
            }
            orderTrip(result.card.prime);
        });
    }catch{
        alert("現在無法購買，請稍後再到此頁面購買，謝謝您。");
    }
}

async function orderTrip(prime) {
    const uName= document.getElementById("uName").value.trim();
    const uEmail = document.getElementById("uEmail").value.trim();
    const uPhone = document.getElementById("uPhone").value.trim();

    const orderJSON = {
            "prime": prime,
            "order":{
                "price": sessionStorage.getItem("price"),
                "trip": {
                    "attraction": {
                        "id": sessionStorage.getItem("attraction_id"),
                        "name": sessionStorage.getItem("attraction_name"),
                        "address": sessionStorage.getItem("attraction_address"),
                        "image": sessionStorage.getItem("attraction_img")
                    },
                    "date": sessionStorage.getItem("date"),
                    "time": sessionStorage.getItem("time")
                },
                "contact": {
                    "name": uName,
                    "email": uEmail,
                    "phone": uPhone
                }
            }
        }

    const token = localStorage.getItem("token");
    const response = await fetch("/api/orders", {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify(orderJSON),
    });

    const dt = await response.json();

    if (!response.ok || dt.error !== undefined){
        alert("建立訂單失敗或其他因素，所以並未建立此訂單，請稍後再試，感謝您。");
    }else{
        // 清除
        sessionStorage.clear();
        const orderNb = dt.data.number;
        window.location.href = `/thankyou?number=${orderNb}`;
    }
}

mutationObs();
async function mutationObs() {
    let builtCount = 0;

    const observerBooking = new MutationObserver(function (mutations) {
        mutations.forEach(function (mutation){
            builtCount++;

            if (builtCount === 4){
                observerBooking.disconnect();
                try{
                    buildPayProcaess();
                }catch{
                    console.log("若要購買，請稍後再試");
                }
            }
        });
    });
    
    const payTag = document.querySelector(".reserve-pay");
    const options = {childList: true};

    observerBooking.observe(payTag, options);
}

mutationObsGetBtn();
async function mutationObsGetBtn(){
    const observeBtn = new MutationObserver(function (mutations) {
        mutations.forEach(function (mutation){
            const buyItinerary = document.getElementById("buyItinerary_btn");
            if (buyItinerary){
                observeBtn.disconnect();
                // 取得APP的資訊，
                buyItinerary.addEventListener("click", function() {
                    const inputStatus = TPDirect.card.getTappayFieldsStatus();
                    
                    if (inputStatus.canGetPrime !== true){
                        alert("請確認輸入的信用卡資訊是否正確，謝謝。");
                        return
                    }

                    getPrimeFromTPD();
                })
            }
        })
    });

    const orderTag = document.querySelector(".reserve-ctn4");
    const options = {childList: true};

    observeBtn.observe(orderTag, options);
}