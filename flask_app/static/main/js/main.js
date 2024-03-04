const full_nav = document.getElementById("full_nav");
const select_button = document.getElementById("select_button");
const select_content = document.getElementById("select_content");
const full_main = document.getElementById("full_main");
const short_main = document.getElementById("short_main");
const feedback_toggle = document.getElementById("feedback_toggle")
const feedback_dialog = document.getElementById("feedback_dialog")
const feedback_form = document.getElementById("feedback_form")



// click feedback toggle
feedback_toggle.addEventListener('click',showFeedbackDialog);

// click menu button
select_button.addEventListener('click',showShortNav);

// submit the feedback_form
feedback_form.onsubmit = function (){
    let name = document.forms["feedback_form"]["name"].value;
    let email = document.forms["feedback_form"]["email"].value;
    let comment = document.forms["feedback_form"]["comment"].value;
    if (name === "") {
        alert("Name is required.");
        return false;
    }
    if (email === "") {
        alert("Email is required.");
        return false;
    }
    if (comment === "") {
        alert("Comment is required.");
        return false;
    }
    return true;
}

// when the website refresh, keep the view stable
window.onload = function (){
    changeShowStyle();
}

// The onresize event is raised when the window or frame is resized.
window.onresize = function(){
    changeShowStyle();
}

// change the style to show when inner width smaller than 650px
function changeShowStyle(){

    if(window.innerWidth <= 1000){
        // navigator part
        full_nav.style.display = "none";
        select_button.style.display = "block";


        // other than home and project page, will not have requirement to change main style
        if(full_main !== null && short_main !== null){
            // main part
            full_main.style.display = "none";
            short_main.style.display = "block";
        }

    }
    else{
        // navigator part
        full_nav.style.display = "block";
        select_button.style.display = "none";
        select_content.style.display = "none";

        // other than home and project page, will not have requirement to change main style
        if(full_main !== null && short_main !== null){
            // main part
            full_main.style.display = "block";
            short_main.style.display = "none";
        }

    }
}

function showShortNav(){
    let status = select_content.style.display;
    if(status === "none" || status === ''){
        select_content.style.display = "flex";
    }
    else{
        select_content.style.display = "none";
    }
}

function showFeedbackDialog(){
    let status = feedback_dialog.style.display;
    if(status === "none" || status === ''){
        feedback_dialog.style.display = "flex";
    }
    else{
        feedback_dialog.style.display = "none";
    }
}