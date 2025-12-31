// 跳出對話視窗
const memberBtn = document.getElementById("member_btn");
const dl = document.querySelector(".logsign_dialog");
const cancel_dl = document.querySelector(".sec_btn");
if (memberBtn){
    memberBtn.addEventListener("click", function() {
        const token = localStorage.getItem("token");
        if (token === null){
            try{
                if (dl){
                    dl.showModal();
                }
            }catch(error){
                console.log("跳出對話視窗失敗。");
            };
        }else{
            localStorage.removeItem("token");
            location.href = location.href;
        }
    });
}

const nm = document.querySelector(".operationPart_name");
const em = document.querySelector(".operationPart_email");
const pw= document.querySelector(".operationPart_pw");
if (cancel_dl){   
    cancel_dl.addEventListener("click", closeDialog);
}

function closeDialog() {
    nm.value = "";
    em.value = "";
    pw.value = "";

    dl.close();
}

// 控制dialog顯示的功能
const clickSign = document.querySelector(".login_signinBtn");
const clickLog = document.querySelector(".signin_loginBtn");
const signRemind = document.querySelector(".dialog_remind_signin");
const logRemind = document.querySelector(".dialog_remind_login");
const signinBtn = document.querySelector(".signin_btn");
const loginBtn = document.querySelector(".login_btn");
const inputNM = document.querySelector(".opt1");
const inputEMText = document.querySelector(".operationPart_email"); 
const dlTitle = document.querySelector(".sec_title");
if (clickSign){
    clickSign.addEventListener("click", function() {
        signRemind.style.display = "block";
        logRemind.style.display = "none";
        signinBtn.style.display = "block";
        loginBtn.style.display = "none";
        inputNM.style.display = "block";
        inputEMText.placeholder = "輸入電子郵件";
        dlTitle.textContent = "註冊會員帳號";

        nm.value = "";
        em.value = "";
        pw.value = "";
        errStr.style.display = "none";
        errStr.textContent = "";
    });
}

if(clickLog){
    clickLog.addEventListener("click", switchToLogin);
}
async function switchToLogin() {
        signRemind.style.display = "none";
        logRemind.style.display = "block";
        signinBtn.style.display = "none";
        loginBtn.style.display = "block";
        inputNM.style.display = "none";
        inputEMText.placeholder = "輸入電子信箱";
        dlTitle.textContent = "登入會員帳號";

        nm.value = "";
        em.value = "";
        pw.value = "";
        errStr.style.display = "none";
        errStr.textContent = "";
}


const errStr = document.querySelector(".dialog_error");
if (loginBtn){
    loginBtn.addEventListener("click", logIn);
}

async function logIn() {
    const emailObj = document.getElementById("emailStr").value.trim();
    const pwObj = document.getElementById("pwStr").value.trim();
    if (emailObj !== "" && pwObj !== ""){
        const jsonDt = {
            "email": emailObj,
            "password": pwObj
        }

        try{
            const response = await fetch("/api/user/auth", {method: "PUT", 
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(jsonDt)
            });

            const data = await response.json();

            if (!response.ok || data.error !== undefined){
                errStr.style.display = "block";
                errStr.textContent = "電子信箱或密碼有錯誤";
            }else{
                localStorage.setItem("token", data.token);
                errStr.style.display = "none";
                memberBtn.textContent = "登出系統";
                closeDialog();
            }
        }catch (error){
                errStr.style.display = "block";
                errStr.textContent = "電子信箱或密碼有錯誤";
        }
    }else{
        errStr.style.display = "block";
        errStr.textContent = "請確認電子信箱與密碼都已填寫";
    }
    
}

if (signinBtn){
    signinBtn.addEventListener("click", signIn);
}

async function signIn() {
    const nameObj = document.getElementById("nameStr").value.trim();
    const emailObj = document.getElementById("emailStr").value.trim();
    const pwObj = document.getElementById("pwStr").value.trim();

    if (nameObj !== "" && emailObj !== "" && pwObj !== ""){
        const jsonDt = {
            "name": nameObj,
            "email": emailObj,
            "password": pwObj
        }

        try{
            const response = await fetch("/api/user", {method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(jsonDt)
            });

            const data = await response.json();

            if (data.ok !== undefined){
                nm.value = "";
                em.value = "";
                pw.value = "";
                errStr.style.display = "block";
                errStr.textContent = "註冊成功，可以登入了";
            }else{
                errStr.style.display = "block";
                errStr.textContent = "電子郵件重複註冊，或其他錯誤";
            }
        }catch (error){
            errStr.style.display = "block";
            errStr.textContent = "註冊過程中，發生執行上的錯誤";
        }
    }else{
        errStr.style.display = "block";
        errStr.textContent = "請確認姓名、電子郵件與密碼都已填寫";
    }
}

// 每次載入都要呼叫確認是否已登入會員
document.addEventListener("DOMContentLoaded", verifyLogged);

async function verifyLogged() {
    try{
        const token = localStorage.getItem("token");

        const response = await fetch("/api/user/auth", {
            method: "GET",
            headers: {"Authorization": `Bearer ${token}`}
        });

        const data = await response.json();

        if (!response.ok || data.data === null){
            // 登出，並移除token
            localStorage.removeItem("token");
            memberBtn.textContent = "登入/註冊";
        }else{
            if (data.data.email !== undefined){
                memberBtn.textContent = "登出系統";
            }else{
                // 驗證沒過
                localStorage.removeItem("token");
                memberBtn.textContent = "登入/註冊";
            }
        }
    }catch (error){
        // 驗證沒過
        localStorage.removeItem("token");
        memberBtn.textContent = "登入/註冊";
    };
};