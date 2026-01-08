// 封裝登入的執行功能
export default class dialogLog {
    // 初始化部分
    constructor(){
        // 跳出對話視窗
        this.memberBtn = document.getElementById("member_btn");
        this.dl = document.querySelector(".logsign_dialog");
        this.cancel_dl = document.querySelector(".sec_btn");
        if (this.memberBtn){
            this.memberBtn.addEventListener("click", () => {
                this.openLoginWindow();
            });
        }

        this.reservedBtn = document.getElementById("shoppingCart_btn");
        if (this.reservedBtn){
            this.reservedBtn.addEventListener("click", () => {
            this.bookingWeb();
            });
        }

        this.nm = document.querySelector(".operationPart_name");
        this.em = document.querySelector(".operationPart_email");
        this.pw= document.querySelector(".operationPart_pw");
        if (this.cancel_dl){   
            this.cancel_dl.addEventListener("click", () => {
                this.closeDialog();
            });
        }

        // 控制dialog顯示的功能
        this.clickSign = document.querySelector(".login_signinBtn");
        this.clickLog = document.querySelector(".signin_loginBtn");
        this.signRemind = document.querySelector(".dialog_remind_signin");
        this.logRemind = document.querySelector(".dialog_remind_login");
        this.signinBtn = document.querySelector(".signin_btn");
        this.loginBtn = document.querySelector(".login_btn");
        this.inputNM = document.querySelector(".opt1");
        this.inputEMText = document.querySelector(".operationPart_email"); 
        this.dlTitle = document.querySelector(".sec_title");
        if (this.clickSign){
            this.clickSign.addEventListener("click", () => {
                this.switchToSign();
            });
        }

        if(this.clickLog){
            this.clickLog.addEventListener("click", () => {
                this.switchToLogin();
            });
        }

        this.errStr = document.querySelector(".dialog_error");

        if (this.loginBtn){
            this.loginBtn.addEventListener("click", () => {
                this.logIn();
            });
        }

        if (this.signinBtn){
            this.signinBtn.addEventListener("click", () => {
                this.signIn();
            });
        }

        // 每次載入都要呼叫確認是否已登入會員
        this.verifyLogged();
    }


    openLoginWindow() {
        const token = localStorage.getItem("token");
        if (token === null){
            try{
                if (this.dl){
                    this.dl.showModal();
                }
            }catch(error){
                console.log("跳出對話視窗失敗。");
            };
        }else{
            localStorage.removeItem("token");
            location.href = location.href;
        }
    }


    bookingWeb() {
        const token = localStorage.getItem("token");
        if (token === null){
            this.openLoginWindow();
        }else{
            window.location.href = `/booking`;
        }
    }


    closeDialog() {
        this.switchToLogin(); // 每次開啟時，都會以登入的畫面呈現
        this.dl.close();
    }
    
    switchToLogin() {
        this.signRemind.style.display = "none";
        this.logRemind.style.display = "block";
        this.signinBtn.style.display = "none";
        this.loginBtn.style.display = "block";
        this.inputNM.style.display = "none";
        this.inputEMText.placeholder = "輸入電子信箱";
        this.dlTitle.textContent = "登入會員帳號";

        this.nm.value = "";
        this.em.value = "";
        this.pw.value = "";
        this.errStr.style.display = "none";
        this.errStr.textContent = "";
    }

    switchToSign() {
        this.signRemind.style.display = "block";
        this.logRemind.style.display = "none";
        this.signinBtn.style.display = "block";
        this.loginBtn.style.display = "none";
        this.inputNM.style.display = "block";
        this.inputEMText.placeholder = "輸入電子郵件";
        this.dlTitle.textContent = "註冊會員帳號";

        this.nm.value = "";
        this.em.value = "";
        this.pw.value = "";
        this.errStr.style.display = "none";
        this.errStr.textContent = "";
    }

    
    async logIn() {
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
                    this.errStr.style.display = "block";
                    this.errStr.textContent = "電子信箱或密碼有錯誤";
                }else{
                    localStorage.setItem("token", data.token);
                    this.errStr.style.display = "none";
                    this.memberBtn.textContent = "登出系統";
                    this.closeDialog();
                }
            }catch (error){
                    this.errStr.style.display = "block";
                    this.errStr.textContent = "電子信箱或密碼有錯誤";
            }
        }else{
            this.errStr.style.display = "block";
            this.errStr.textContent = "請確認電子信箱與密碼都已填寫";
        }
        
    }

    
    async signIn() {
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
                    this.nm.value = "";
                    this.em.value = "";
                    this.pw.value = "";
                    this.errStr.style.display = "block";
                    this.errStr.textContent = "註冊成功，可以登入了";
                }else{
                    this.errStr.style.display = "block";
                    this.errStr.textContent = "電子郵件重複註冊，或其他錯誤";
                }
            }catch (error){
                this.errStr.style.display = "block";
                this.errStr.textContent = "註冊過程中，發生執行上的錯誤";
            }
        }else{
            this.errStr.style.display = "block";
            this.errStr.textContent = "請確認姓名、電子郵件與密碼都已填寫";
        }
    }

    async verifyLogged() {
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
                this.memberBtn.textContent = "登入/註冊";
            }else{
                if (data.data.email !== undefined){
                    this.memberBtn.textContent = "登出系統";
                }else{
                    // 驗證沒過
                    localStorage.removeItem("token");
                    this.memberBtn.textContent = "登入/註冊";
                }
            }
        }catch (error){
            // 驗證沒過
            localStorage.removeItem("token");
            this.memberBtn.textContent = "登入/註冊";
        };
    };
}

// 建立實例
export const dialogUI = new dialogLog();
