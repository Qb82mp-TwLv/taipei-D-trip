let totalImgLenght = null;
attractionInfo();

async function attractionInfo() {
  const urlStr = new URL(window.location.href);
  const urlPathname = String(urlStr.pathname);
  const urlPathnameSplit = urlPathname.split("/");
  const attId = parseInt(urlPathnameSplit[2], 10);
  let attInfo = null;

  console.log(attId);
  await Promise.all([fetch(`/api/attraction/${attId}`, {method: "GET"})
    .then(response => {
      return response.json();
    }).catch(error => {
      console.log("取景點資訊發生錯誤:", error);
  })]).then(data => {
    attInfo=data[0].data;
  });

  console.log(attInfo);

  imgSlideShow(attInfo.images);

  const name = attInfo.name;
  const CATandMRTStr = attInfo.category+" at "+ attInfo.mrt;
  imgOrderText(name, CATandMRTStr);

  imgIntroInfo(attInfo.description, attInfo.address, attInfo.transport);
}

// 將景點圖片都顯示於此功能中(image slideshow)
async function imgSlideShow(arr) {
  const slideCTN = document.getElementById("imgItem");
  const slideBarCTN = document.getElementById("slideLine");
  if (slideCTN && slideBarCTN){
    if (arr.length > 0){
      for (i in arr){
        // 範例
        // <div class="img-width-fat">
        //   <img src="圖片網址">
        // </div>
        const newTagImgCTNDiv = document.createElement("div");
        newTagImgCTNDiv.classList.add("img-width-fat");
        const newTagImg = document.createElement("img");
        newTagImg.src = arr[i];

        newTagImgCTNDiv.appendChild(newTagImg);

        // 範例
        // <div class="slide-line lineleft-radius" id="0"></div>
        // <div class="slide-line" id="1"></div>
        // <div class="slide-line lineright-radius" id="2"></div>
        const newTagBarItem = document.createElement("div");
        if (i === "0"){
          newTagBarItem.className = "slide-line lineleft-radius";
          newTagBarItem.style.backgroundColor = `rgba(0, 0, 0, 0.8)`;
        }else if (i === String(parseInt(arr.length-1))){
          newTagBarItem.className = "slide-line lineright-radius";
        }else{
          newTagBarItem.className="slide-line";
        };
        newTagBarItem.id = i;

        slideCTN.appendChild(newTagImgCTNDiv);
        slideBarCTN.appendChild(newTagBarItem);
      }

      totalImgLenght = arr.length;
    }
  }
};

// 將景點名稱&分類&捷運站都顯示出來
async function imgOrderText(Str1, Str2) {
  const attName = document.querySelector(".imgName");
  const attCATandMRT = document.querySelector(".imgCAT");
  if (attName){
    attName.textContent = Str1;
  }

  if (attCATandMRT){
    attCATandMRT.textContent = Str2;
  }
}

// 將景點的介紹與相關說明顯示出來
async function imgIntroInfo(Str1, Str2, Str3) {
  const introStr = document.getElementById("attIntroStr");
  const addressStr = document.getElementById("attAddressStr");
  const trafficStr = document.getElementById("attTrafficStr");
  if (introStr){
    introStr.textContent = Str1;
  }

  if(addressStr){
    addressStr.textContent = Str2;
  }

  if(trafficStr){
    trafficStr.textContent = Str3;
  }
}

let imgIdx = 0;
const imgSlides = document.querySelector(".imgSlides");

function slideLeftBtn() {
  let imgslideX = null;
  // 負責圖片為第幾張的功能
  let slideLineOld = document.getElementById(String(imgIdx));
  let slideLineNew = null;
  if (imgIdx !== 0){
    imgIdx--;
    slideLineNew = document.getElementById(String(imgIdx));
    
    imgslideX = imgIdx * 100;

    imgSlides.style.transform = `translateX(-${imgslideX}%)`;
    
    slideLineNew.style.backgroundColor = `rgba(0, 0, 0, 0.8)`;
    slideLineOld.style.backgroundColor = `rgba(255, 255, 255, 0.5)`;
  }
}

function slideRightBtn() {
  let imgslideX = null;
  let slideLineOld = document.getElementById(String(imgIdx));
  let slideLineNew = null;

  if (imgIdx !== (totalImgLenght-1)){
    imgIdx++;
    slideLineNew = document.getElementById(String(imgIdx));
  
    imgslideX = imgIdx * 100;

    imgSlides.style.transform = `translateX(-${imgslideX}%)`;
    
    slideLineNew.style.backgroundColor = `rgba(0, 0, 0, 0.8)`;
    slideLineOld.style.backgroundColor = `rgba(255, 255, 255, 0.5)`;
  }
}


const slideL = document.getElementById("slideLeft");
if (slideL){
  slideL.addEventListener("click", slideLeftBtn);
}
const slideR = document.getElementById("slideRight");
if (slideR){
  slideR.addEventListener("click", slideRightBtn);
}


// 當選擇時間在切換時，需要執行的過程
const radioAM = document.getElementById("selectAM");
const orderPrice = document.getElementById("ordPrice");
if (radioAM){
  radioAM.addEventListener("click", function() {
    if (orderPrice){
      orderPrice.textContent = "新台幣 2000 元";
    }
  });
}

const radioPM = document.getElementById("selectPM");
if (radioPM){
  radioPM.addEventListener("click", function() {
    if (orderPrice){
      orderPrice.textContent = "新台幣 2500 元";
    }
  });
}

const homePage = document.querySelector(".Nav-title");
if (homePage){
  homePage.addEventListener("click", function() {
    window.location.href = `/`;
  });
}


