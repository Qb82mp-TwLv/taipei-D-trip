// 點擊"台北一日遊"的文字，會返回主頁
const homePage = document.querySelector(".Nav-title");
if (homePage){
  homePage.addEventListener("click", function() {
    window.location.href = `/`;
  });
}

verifyMemberShip();

// 先確認有登入的狀態
async function verifyMemberShip(){
  const token = localStorage.getItem("token");
  try{
    if (token === null){
      window.location.href = `/`;
    }else{
      const response = await fetch("/api/user/auth", {
        method: "GET",
        headers: {"Authorization": `Bearer ${token}`}
      });

      const memb = await response.json();

      if (!response.ok || memb.data === null){
        window.location.href = "/";
      }else{
        getReserveInfo(memb.data.name, memb.data.email);
      }
    }
  }catch{
    window.location.href = "/";
  }
}

// 撈取預定行程的資訊
async function getReserveInfo(name, email){
  try{
    const token = localStorage.getItem("token");
    const response = await fetch("/api/booking", {
      method: "GET",
      headers: {"Authorization": `Bearer ${token}`}
    });

    const dt = await response.json();

    if (!response.ok || dt.data === null){
      reserveBlockOne(null, name);
    }else{
      reserveBlockOne(dt.data, name);
      reserveBlockTwo(name, email);
      reserveBlockThree();
      reserveBlockFour(dt.data.price);
    }

  }catch(error){
    console.log("發生錯誤");
    reserveBlockOne(null, name);
  }
}

// 根據是否有預定行程的資料，建立預定行程的頁面(第一區塊)
async function reserveBlockOne(dt, NM){
  const imgStr = document.querySelector(".itinerary-imgStr");
  const userNM = document.querySelector(".userNM");
  const viewImgStr = document.querySelector(".imgStr-img");
  if (imgStr){
    try{ 
      if (dt === null){
        userNM.textContent = String(NM);
        viewImgStr.textContent = "目前沒有任何待預訂的行程";
        reviseStyle();
      }else{
        userNM.textContent = String(NM);

        const newImgTag = new Image();
        newImgTag.src = dt.attraction.image;
        viewImgStr.appendChild(newImgTag);

        const newImgTextTag = document.createElement("div");
        newImgTextTag.classList.add("imgStr-text");
        // 顯示該景點的相關文字資訊
        const newTextTitleTag = document.createElement("div");
        newTextTitleTag.classList.add("text-title");
        newTextTitleTag.textContent = `台北一日遊：${String(dt.attraction.name)}`;
        // 日期部分
        const newTextDateTag = document.createElement("div");
        newTextDateTag.classList.add("text-date");
        // 日期的標籤下的其他標籤
        const newDateTitleTag = document.createElement("div");
        newDateTitleTag.classList.add("title-bold");
        newDateTitleTag.textContent = "日期：";
        const newDateContentTag = document.createElement("div");
        newDateContentTag.classList.add("content-medium");
        newDateContentTag.textContent = String(dt.date);
        newTextDateTag.appendChild(newDateTitleTag);
        newTextDateTag.appendChild(newDateContentTag);
        
        // 時間部分
        const newTextTimeTag = document.createElement("div");
        newTextTimeTag.classList.add("text-time");
        // 時間的標籤下的其他標籤
        const newTimeTitleTag = document.createElement("div");
        newTimeTitleTag.classList.add("title-bold");
        newTimeTitleTag.textContent = "時間：";
        const newTimeContentTag = document.createElement("div");
        newTimeContentTag.classList.add("content-medium");
        if (String(dt.time) === "afternoon"){
          newTimeContentTag.textContent = "下午2點到晚上9點";
        }else if(String(dt.time) === "morning"){
          newTimeContentTag.textContent = "早上9點到下午4點";
        }
        newTextTimeTag.appendChild(newTimeTitleTag);
        newTextTimeTag.appendChild(newTimeContentTag);

        // 費用部分
        const newTextPriceTag = document.createElement("div");
        newTextPriceTag.classList.add("text-price");
        // 費用的標籤下的其他標籤
        const newPriceTitleTag = document.createElement("div");
        newPriceTitleTag.classList.add("title-bold");
        newPriceTitleTag.textContent = "費用：";
        const newPriceContentTag = document.createElement("div");
        newPriceContentTag.classList.add("content-medium");
        newPriceContentTag.textContent = `新台幣 ${String(dt.price)} 元`;
        newTextPriceTag.appendChild(newPriceTitleTag);
        newTextPriceTag.appendChild(newPriceContentTag);

        // 地點部分
        const newTextAddressTag = document.createElement("div");
        newTextAddressTag.classList.add("text-adress");
        // 地點的標籤下的其他標籤
        const newAddressTitleTag = document.createElement("div");
        newAddressTitleTag.classList.add("title-bold");
        newAddressTitleTag.textContent = "地點：";
        const newAddressContentTag = document.createElement("div");
        newAddressContentTag.classList.add("content-medium");
        newAddressContentTag.textContent = String(dt.attraction.address);
        newTextAddressTag.appendChild(newAddressTitleTag);
        newTextAddressTag.appendChild(newAddressContentTag);

        newImgTextTag.appendChild(newTextTitleTag);
        newImgTextTag.appendChild(newTextDateTag);
        newImgTextTag.appendChild(newTextTimeTag);
        newImgTextTag.appendChild(newTextPriceTag);
        newImgTextTag.appendChild(newTextAddressTag);

        // 刪除的按鈕
        const delBtn = document.createElement("div");
        delBtn.classList.add("itinerary-del");
        const delImg = document.createElement("img");
        delImg.src = "/static/img/icon_delete.png";
        delImg.addEventListener("click", delBookInfo);
        //delBtn.textContent = "del";
        delBtn.appendChild(delImg);

        // 將標籤新增進第一區塊
        imgStr.appendChild(viewImgStr);
        imgStr.appendChild(newImgTextTag);
        imgStr.appendChild(delBtn);
      };
    }catch{
      const userNM = document.querySelector(".userNM");
      userNM.textContent = String(NM);
      viewImgStr.textContent = "目前沒有任何待預訂的行程";
    };
  };
};


// 根據是否有預定行程的資料，建立預定行程的頁面(第二區塊)
async function reserveBlockTwo(NM, Em){
  const viewContact = document.querySelector(".reserve-contact");
  if (viewContact){
    try{
      // 聯絡資訊的主標題
      const newContactTitleTag = document.createElement("div");
      newContactTitleTag.classList.add("contact-title");
      newContactTitleTag.textContent = "您的聯絡資訊";
      // 聯絡姓名部分
      const newNameTag = document.createElement("div");
      newNameTag.classList.add("contact-name");
      // 聯絡姓名的標籤下的其他標籤
      const newNameTitleTag = document.createElement("div");
      newNameTitleTag.textContent = "聯絡姓名：";
      const newNameInputTag = document.createElement("input");
      newNameInputTag.type = "text";
      newNameInputTag.classList.add("contact-input");
      newNameInputTag.value = String(NM);
      newNameTag.appendChild(newNameTitleTag);
      newNameTag.appendChild(newNameInputTag);

      // 聯絡信箱部分
      const newEmailTag = document.createElement("div");
      newEmailTag.classList.add("contact-email");
      // 聯絡信箱的標籤下的其他標籤
      const newEmailTitleTag = document.createElement("div");
      newEmailTitleTag.textContent = "聯絡信箱：";
      const newEmailInputTag = document.createElement("input");
      newEmailInputTag.type = "email";
      newEmailInputTag.classList.add("contact-input");
      newEmailInputTag.value = String(Em);
      newEmailTag.appendChild(newEmailTitleTag);
      newEmailTag.appendChild(newEmailInputTag);

      // 手機號碼部分
      const newMobileTag = document.createElement("div");
      newMobileTag.classList.add("contact-mobile");
      // 手機號碼的標籤下的其他標籤
      const newMobileTitleTag = document.createElement("div");
      newMobileTitleTag.textContent = "手機號碼：";
      const newMobileInputTag = document.createElement("input");
      newMobileInputTag.type = "tel";
      newMobileInputTag.classList.add("contact-input");
      newMobileTag.appendChild(newMobileTitleTag);
      newMobileTag.appendChild(newMobileInputTag);

      // 備註資訊
      const newRemarkTag = document.createElement("div");
      newRemarkTag.classList.add("contact-remark");
      newRemarkTag.textContent = "請保持手機暢通，準時到達，導覽人員將用手機與您聯繫，務必留下正確的聯絡方式。";

      viewContact.appendChild(newContactTitleTag);
      viewContact.appendChild(newNameTag);
      viewContact.appendChild(newEmailTag);
      viewContact.appendChild(newMobileTag);
      viewContact.appendChild(newRemarkTag);
    }catch{
      viewContact.textContent= "抱歉，發生錯誤，請稍後再試。";
    };
  };
};


// 根據是否有預定行程的資料，建立預定行程的頁面(第三區塊)
async function reserveBlockThree(){
  const viewPay = document.querySelector(".reserve-pay");
  if (viewPay){
    try{
      // 信用卡付款資訊的主標題
      const newPayTitleTag = document.createElement("div");
      newPayTitleTag.classList.add("pay-title");
      newPayTitleTag.textContent = "信用卡付款資訊";
      // 卡片部分
      const newNumberTag = document.createElement("div");
      newNumberTag.classList.add("pay-number");
      // 卡片的標籤下的其他標籤
      const newNumberTitleTag = document.createElement("div");
      newNumberTitleTag.textContent = "卡片號碼：";
      const newNumberInputTag = document.createElement("input");
      newNumberInputTag.type = "text";
      newNumberInputTag.classList.add("pay-input");
      newNumberInputTag.classList.add("pay-input-weight");
      newNumberInputTag.placeholder = "**** **** **** ****";
      newNumberInputTag.maxLength = "19";
      newNumberInputTag.autocomplete = "cc-number";
      newNumberTag.appendChild(newNumberTitleTag);
      newNumberTag.appendChild(newNumberInputTag);

      // 過期時間部分
      const newTimeTag = document.createElement("div");
      newTimeTag.classList.add("pay-time");
      // 過期時間的標籤下的其他標籤
      const newTimeTitleTag = document.createElement("div");
      newTimeTitleTag.textContent = "過期時間：";
      const newTimeInputTag = document.createElement("input");
      newTimeInputTag.type = "text";
      newTimeInputTag.classList.add("pay-input");
      newTimeInputTag.classList.add("pay-input-weight");
      newTimeInputTag.placeholder = "MM / YY";
      newTimeTag.appendChild(newTimeTitleTag);
      newTimeTag.appendChild(newTimeInputTag);

      // 驗證密碼部分
      const newPwTag = document.createElement("div");
      newPwTag.classList.add("pay-pw");
      // 驗證密碼的標籤下的其他標籤
      const newPwTitleTag = document.createElement("div");
      newPwTitleTag.textContent = "驗證密碼：";
      const newPwInputTag = document.createElement("input");
      newPwInputTag.type = "password";
      newPwInputTag.classList.add("pay-input");
      newPwInputTag.classList.add("pay-input-weight");
      newPwInputTag.placeholder = "CVV";
      newPwTag.appendChild(newPwTitleTag);
      newPwTag.appendChild(newPwInputTag);

      viewPay.appendChild(newPayTitleTag);
      viewPay.appendChild(newNumberTag);
      viewPay.appendChild(newTimeTag);
      viewPay.appendChild(newPwTag);
    }catch{
      viewPay.textContent = "抱歉，發生錯誤，請稍後再試。";
    }
  };
};

// 根據是否有預定行程的資料，建立預定行程的頁面(第三區塊)
async function reserveBlockFour(priceStr){
  const reservedCTN4 = document.querySelector(".reserve-ctn4");
  if (reservedCTN4){
    const reservedOrd = document.createElement("div");
    reservedOrd.classList.add("reserve-order");
    // 顯示總價的部分
    const totalPrice = document.createElement("div");
    totalPrice.textContent = `總價：新台幣 ${String(priceStr)} 元`;
    const buyBtn = document.createElement("button");
    buyBtn.classList.add("buy_btn");
    buyBtn.id = "buyItinerary_btn";
    buyBtn.textContent = "確認訂購並付款";
    // 將文字與按鈕新增到reservedOrd標籤下
    reservedOrd.appendChild(totalPrice);
    reservedOrd.appendChild(buyBtn);

    reservedCTN4.appendChild(reservedOrd);
  }
}


// 刪除資訊
async function delBookInfo() {
  try{
    const token = localStorage.getItem("token");

    if (token !== null){
      const response = await fetch("/api/booking", {
        method: "DELETE",
        headers: {"Authorization": `Bearer ${token}`}
      });

      const reuslt = await response.json();

      if (!response.ok || reuslt.error !== undefined){
        console.log("失敗");
        alert("刪除失敗，請稍後再試。");
      }else{
        const viewImgStr = document.querySelector(".imgStr-img");
        const viewContact = document.querySelector(".reserve-contact");
        const viewPay = document.querySelector(".reserve-pay");
        const reservedCTN4 = document.querySelector(".reserve-ctn4");

        if (viewImgStr && viewContact && viewPay){
          // 刪除新增的子標籤
          viewImgStr.removeChild(viewImgStr.firstChild);
          viewContact.removeChild(viewContact.firstChild);
          viewPay.removeChild(viewPay.firstChild);
          reservedCTN4.removeChild(reservedCTN4.firstChild);

          viewImgStr.textContent = "目前沒有任何待預訂的行程";
          reviseStyle();
          // 重新執行設定頁面
          location.reload();
        }
      }
    }
  }catch{
    alert("刪除失敗，請稍後再試。");
  };
};


async function reviseStyle() {
  const reservedCTN1 = document.querySelector(".reserve-ctn1");
  reservedCTN1.style.height = "13rem";
  reservedCTN1.style.borderBottom = "0px";
  const itineraryImg = document.querySelector('.itinerary-imgStr');
  itineraryImg.style.height = "3rem";
  itineraryImg.style.gridTemplateColumns = "minmax(1rem, max-content)";
  itineraryImg.style.gridTemplateRows = "minmax(1rem, max-content)";

  const imgStr = document.querySelector(".imgStr-img");
  imgStr.style.height = "2.2rem";
  imgStr.style.paddingLeft = "0";

  const reservedCTN2 = document.querySelector(".reserve-ctn2");
  reservedCTN2.style.height = "0";
  reservedCTN2.style.borderBottom = "0px";
  const viewContact = document.querySelector(".reserve-contact");
  viewContact.style.height ="0";
  viewContact.style.padding = "0";

  const reservedCTN3 = document.querySelector(".reserve-ctn3");
  reservedCTN3.style.height = "0";
  reservedCTN3.style.borderBottom = "0px";
  const viewPay = document.querySelector(".reserve-pay");
  viewPay.style.height = "0";
  viewPay.style.padding = "0";

  const reservedCTN4 = document.querySelector(".reserve-ctn4");
  reservedCTN4.style.height = "0";
  
  const footer = document.querySelector("footer");
  footer.classList.add("footer-height");
}