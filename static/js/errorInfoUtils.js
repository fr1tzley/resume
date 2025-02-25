function hideErrorInfo() {
    let errorBar = document.getElementById("error-bar");
    let infoBar = document.getElementById("info-bar");
    if (errorBar) {
        errorBar.style.display = "none";

    }
    if (infoBar) {
        infoBar.style.display = "none";
    }
        
}

function showBarWithMsg(id,msg) {
    let bar = document.getElementById(id)        
    bar.style.display = "block"
    bar.innerText = msg
}