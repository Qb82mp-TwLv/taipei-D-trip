const dropList = document.getElementById("dropItem");
async function selectCAT() {
    if (dropList){
        dropList.classList.toggle('active');
    }
    else{
        console.log("抱歉，沒有找到此物件。");
    }
}

// 執行顯示category選項的顯示功能
const clickCAT = document.getElementById("selectCategory");
if (clickCAT){
        clickCAT.addEventListener("click", selectCAT);
}

const categoryDropDown = document.getElementById("searchDropList");
if (categoryDropDown){
    catgoryDrop();
}

// 執行取category的功能
async function catgoryDrop() {
    const categoryNm = document.getElementById("categoryName");

    await fetch("/api/categories", {method: "GET"})
    .then(response => {
        return response.json();
    })
    .then(data => {
        const list = data.data;
        if (list.length !== 0){
            const newTagLiAll = document.createElement("li");
            newTagLiAll.classList.add("option");
            newTagLiAll.textContent = "全部分類";
            categoryDropDown.appendChild(newTagLiAll);
            newTagLiAll.addEventListener("click", function(){
                if(categoryNm){
                    categoryNm.textContent = "全部分類";
                    selectCAT();
                }
            });

            for(val in list){
                let newTagLi = document.createElement("li");
                newTagLi.classList.add("option");
                newTagLi.textContent = String(list[val]);

                categoryDropDown.appendChild(newTagLi);

                // 設定選取分類的名稱
                newTagLi.addEventListener("click", function(){
                    if (categoryNm){
                        let text = newTagLi.textContent;
                        categoryNm.textContent = text;
                        selectCAT();
                    }
                });
            }
        }
        else{
            console.log("抱歉，取分類的名稱時發生錯誤。");
        }
    })
    .catch(error =>{
        console.log("取分類的名稱出現錯誤:", error);
    });
};


//輸入框監控
const inputActive = document.getElementById("searInpt");
if (inputActive){
    inputActive.addEventListener("input", function() {
        if (inputActive.style.color !== "rgb(0, 0, 0)"){
            inputActive.style.color = "#000";
        }
    }, {once:true});
}

// 控制ListBar的左右滑動功能
const barLeftButton = document.getElementById("barLeftBtn");
if (barLeftButton){
    barLeftButton.addEventListener("click", function() {
        const mrtScrollLeft = document.getElementById("mrtItemScorll");
        if (mrtScrollLeft){
            mrtScrollLeft.scrollLeft -= 60;
        }else{
            console.log("抱歉，往左滑動出現錯誤。");
        }
    });
}

const barRightButton = document.getElementById("barRightBtn");
if (barRightButton){
    barRightButton.addEventListener("click", function() {
        const mrtScrollRight = document.getElementById("mrtItemScorll");
        if (mrtScrollRight){
            mrtScrollRight.scrollLeft += 60;
        }else{
            console.log("抱歉，往右滑動出現錯誤。");
        }
    });
}

// 使用mrt的資料動態新增捷運站的值
const mrtItem = document.getElementById("mrtCTN");
if (mrtItem){
    marListBar();
};

async function marListBar() {
    await fetch("/api/mrts", {method:"GET"})
    .then(response => {
        return response.json();
    })
    .then(dt => {
        const mrtNmList = dt.data;

        if (mrtNmList.length > 0){
            for (i in mrtNmList){
                let newTagMrtNm = document.createElement("li");
                newTagMrtNm.classList.add("mrt-option");
                newTagMrtNm.textContent = String(mrtNmList[i]);

                mrtItem.appendChild(newTagMrtNm);

                // 新增點擊功能
                newTagMrtNm.addEventListener("click", function() {
                    const searchKw = document.getElementById("searInpt");
                    if (searchKw){
                        if (searchKw.style.color !== "rgb(0, 0, 0)"){
                            searchKw.style.color = "#000";
                        }

                        const mrtNameStr = newTagMrtNm.textContent;
                        searchKw.value = mrtNameStr;
                        searchATT();
                    }else{
                        console.log("選取MRT發生錯誤");
                    }
                });
            };
        };
    })
    .catch(err => {
        console.log("抱歉，在取得捷運名稱時發生錯誤:", err);
    });
};


// 此陣列用來判斷是否有重複呼叫的page頁面，第一次被呼叫都會寫進此陣列中
let nextPageArr = [];
// 紀錄是否有下一頁 
let nextPage = 0;


async function searchATT() { 
    const CAT = document.getElementById("categoryName");
    const mrtNmStr = document.getElementById("searInpt"); 
    let searchStr = "";
    nextPageArr = [];

    // 分類與關鍵字的部分
    if (CAT && mrtNmStr){
        if (CAT.textContent === "全部分類"){
            if (mrtNmStr.value === "" || mrtNmStr.value === "輸入景點名稱查詢"){
                searchStr = "?page="+String(0);
            }else{
                searchStr = "?page="+String(0)+"&keyword="+mrtNmStr.value;
            };  
        }
        else{
            if (mrtNmStr.value === "" || mrtNmStr.value === "輸入景點名稱查詢"){
                searchStr = "?page="+String(0)+"&category="+CAT.textContent;
            }
            else{
                searchStr = "?page="+String(0)+"&category="+CAT.textContent+"&keyword="+mrtNmStr.value;
            };
        };
    };

    try{
        // 延遲300毫秒
        await new Promise(delay => setTimeout(delay, 300));

        const response = await fetch("/api/attractions"+searchStr, {method: "GET"})
        if (!response.ok){
            console.log("抱歉，在查詢類別與關鍵字時，發生查詢錯誤，請稍後再試。");
        }

        const dtJson = await response.json();
        removeATTImg();
        if ("data" in dtJson){
            nextPageArr.push(0);
            nextPage = dtJson.nextPage;
            viewATTImg(dtJson.data);
        }else if ("error" in dtJson){
            notFoundATT();
        }
    }catch (err){
        console.log("抱歉，在查詢類別與關鍵字時，發生查詢錯誤，請稍後再試。");
    };
};

// 使用搜尋按鈕搜尋景點資訊
const searBtn = document.getElementById("searBtn");
if (searBtn){
    searBtn.addEventListener("click", searchATT);
};


// 清除原本的景點資訊
async function removeATTImg(){
    // 先將原本的移除
    const imgBlock = document.querySelectorAll(".img-block");
    if (imgBlock){
        // 使用forEach的遍歷方式迴圈
        imgBlock.forEach(element => {
            if(element){
                element.parentNode.removeChild(element);
            }
        });
    };

    // 將無查詢的資料移除
    const strBlock = document.querySelectorAll(".noD-content");
    if (strBlock){
        strBlock.forEach(element => {
            if (element){
                element.parentNode.removeChild(element);
            }
        });
    };
};

// 將景點資料顯示於頁面中間
async function viewATTImg(attInfo) {
    const attImgCTN = document.getElementById("imgCTN");
    if (attImgCTN){
        if (attInfo.length > 0){
            for (i in attInfo){
                let newTagBlock = document.createElement("div");
                newTagBlock.classList.add("img-block");

                let newTagTitle = document.createElement("div");
                newTagTitle.classList.add("img-title");
                let newTagFile = document.createElement("img");
                newTagFile.classList.add("img-file");
                newTagFile.src = attInfo[i].images[0];
                let newTagTitleName = document.createElement("div");
                newTagTitleName.classList.add("title-name");
                let newTagNameStr = document.createElement("span");
                newTagNameStr.textContent = String(attInfo[i].name);
                newTagTitleName.appendChild(newTagNameStr);
                newTagTitle.appendChild(newTagFile);
                newTagTitle.appendChild(newTagTitleName);

                let newTagInfo = document.createElement("div");
                newTagInfo.classList.add("img-info");
                let newInfoFW = document.createElement("div");
                newInfoFW.classList.add("img-info-fw");
                let newTagMRT = document.createElement("div");
                if (attInfo[i].mrt === null){
                    newTagMRT.textContent = String("無");
                }else{
                    newTagMRT.textContent = String(attInfo[i].mrt);
                }
                
                let newTagCategory = document.createElement("div");
                newTagCategory.textContent = String(attInfo[i].category);
                newInfoFW.appendChild(newTagMRT);
                newInfoFW.appendChild(newTagCategory);
                newTagInfo.appendChild(newInfoFW);

                newTagBlock.appendChild(newTagTitle);
                newTagBlock.appendChild(newTagInfo);

                attImgCTN.appendChild(newTagBlock);
            };
        };
    };
};


// 若沒有資料要顯示無查詢到相關資料的解釋
async function notFoundATT(){
    const attCTN = document.getElementById("imgFW");
    if (attCTN){
        const newTagBlock = document.createElement("div");
        newTagBlock.classList.add("noD-content");

        const newTagStr = document.createElement("div");
        newTagStr.textContent = "抱歉，無查詢到相關資料";
        newTagBlock.appendChild(newTagStr);

        attCTN.appendChild(newTagBlock);
    };
};


// 設定滑軌可見footer的部分
async function callLoadingATT(tag) {
    // 使用isIntersecting的方式判斷該物件，是否有根據條件全部顯示在視窗中，
    // 若全部顯示於視窗中，才會繼續往下執行
    if (tag[0].isIntersecting){
        if (nextPage !== null && nextPageArr.includes(nextPage) !== true){
            const CAT = document.getElementById("categoryName");
            const mrtNmStr = document.getElementById("searInpt"); 
            let searchStr = "";
            // 儲存當下要執行的頁碼
            nextPageArr.push(nextPage);

            // 分類與關鍵字的部分
            if (CAT && mrtNmStr){
                if (CAT.textContent === "全部分類"){
                    if (mrtNmStr.value === "" || mrtNmStr.value === "輸入景點名稱查詢"){
                        searchStr = "?page="+String(nextPage);
                    }else{
                        searchStr = "?page="+String(nextPage)+"&keyword="+mrtNmStr.value;
                    };  
                }
                else{
                    if (mrtNmStr.value === "" || mrtNmStr.value === "輸入景點名稱查詢"){
                        searchStr = "?page="+String(nextPage)+"&category="+CAT.textContent;
                    }
                    else{
                        searchStr = "?page="+String(nextPage)+"&category="+CAT.textContent+"&keyword="+mrtNmStr.value;
                    };
                };
            };

            try{
                // 延遲300毫秒
                await new Promise(delay => setTimeout(delay, 300));

                const response = await fetch("/api/attractions"+searchStr, {method: "GET"})
                if (!response.ok){
                    console.log("抱歉，在查詢類別與關鍵字時，發生查詢錯誤，請稍後再試。");
                }

                const dtJson = await response.json();
                // removeATTImg();
                if ("data" in dtJson){
                    nextPage = dtJson.nextPage;
                    viewATTImg(dtJson.data);
                }else if ("error" in dtJson){
                    notFoundATT();
                }
            }catch (err){
                console.log("抱歉，在查詢類別與關鍵字時，發生查詢錯誤，請稍後再試。");
            };
        }
    }
}


scrollLoading();
// 監控滑軌是否footer的部分有全部出現在viewport
async function scrollLoading() {
    const opt = {
        threshold:[1]
    };
    let observer = new IntersectionObserver(callLoadingATT, opt);

    const footerTag = document.getElementById("footerBlock");
    if(footerTag){
        observer.observe(footerTag);
    }
}

