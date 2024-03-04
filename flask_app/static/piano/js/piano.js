// hover area
const hoverInBlackText = document.getElementsByClassName("hover_text_in_black");
const hoverInWhiteText = document.getElementsByClassName("hover_text_in_white");
const hoverArea = document.getElementById("piano_key_area");

// advent
const greatOne = document.getElementById("great_one");
const strangeTitle= document.getElementById("strange_title");
const awakeTitle = document.getElementById("awake");


// audio part
const sound = {
    "KeyA":"http://carolinegabriel.com/demo/js-keyboard/sounds/040.wav",
    "KeyW":"http://carolinegabriel.com/demo/js-keyboard/sounds/041.wav",
    "KeyS":"http://carolinegabriel.com/demo/js-keyboard/sounds/042.wav",
    "KeyE":"http://carolinegabriel.com/demo/js-keyboard/sounds/043.wav",
    "KeyD":"http://carolinegabriel.com/demo/js-keyboard/sounds/044.wav",
    "KeyF":"http://carolinegabriel.com/demo/js-keyboard/sounds/045.wav",
    "KeyT":"http://carolinegabriel.com/demo/js-keyboard/sounds/046.wav",
    "KeyG":"http://carolinegabriel.com/demo/js-keyboard/sounds/047.wav",
    "KeyY":"http://carolinegabriel.com/demo/js-keyboard/sounds/048.wav",
    "KeyH":"http://carolinegabriel.com/demo/js-keyboard/sounds/049.wav",
    "KeyU":"http://carolinegabriel.com/demo/js-keyboard/sounds/050.wav",
    "KeyJ":"http://carolinegabriel.com/demo/js-keyboard/sounds/051.wav",
    "KeyK":"http://carolinegabriel.com/demo/js-keyboard/sounds/052.wav",
    "KeyO":"http://carolinegabriel.com/demo/js-keyboard/sounds/053.wav",
    "KeyL":"http://carolinegabriel.com/demo/js-keyboard/sounds/054.wav",
    "KeyP":"http://carolinegabriel.com/demo/js-keyboard/sounds/055.wav",
    "KeySemicolon":"http://carolinegabriel.com/demo/js-keyboard/sounds/056.wav"
};

const audio = new Audio();

// input sequence list
let input_string = "";
let shut_down = false;




// hover the key area then show the keyboard letter
hoverArea.onmouseover = function (){
    for(let index = 0; index<hoverInBlackText.length; index++){
        hoverInBlackText[index].style.display = "block";
    }
    for(let index = 0; index<hoverInWhiteText.length; index++){
        hoverInWhiteText[index].style.display = "block";
    }
}
hoverArea.onmouseout = function (){
    for(let index = 0; index<hoverInBlackText.length; index++){
        hoverInBlackText[index].style.display = "none";
    }
    for(let index = 0; index<hoverInWhiteText.length; index++){
        hoverInWhiteText[index].style.display = "none";
    }
}

//keyboard active
window.onkeydown = function (e){
    if(!shut_down){
        let key = getKeyValue(e.code);
        // key block get smaller when keydown
        document.getElementById(key).style.transform = "scale(0.85,0.95)";

        // play audio
        audio.src = sound[key];
        //check the voice is successes.
        let res = audio.play();

        input_string += e.key;
        checkArray();
    }
}

window.onkeyup = function (e){
    if(!shut_down){
        let key = getKeyValue(e.code);
        document.getElementById(key).style.transform = "none";
    }
}


// justify the array with correct sequence
function checkArray(){
    let target = "weseeyou";

    // check input each times
    for(let index = 0; index < input_string.length; index++){
        // clear the input string when it not correct order
        if(input_string[index] !== target[index]){
            input_string = "";
            break;
        }
    }
    //target achieved
    if(input_string === "weseeyou"){
        advent();
        input_string = "";
    }
}

function advent(){
    // cannot play piano if awake
    shut_down = true;

    // show the great one and title and music
    greatOne.style.display = "block";
    awakeTitle.style.display = "block";
    strangeTitle.style.display = "none";

    // delay to play creepy audio
    setTimeout(function (){
        audio.src = "static/piano/documents/Creepy-piano-sound-effect.mp3";
        // check the voice is successes.
        let res = audio.play();
    },400);

}


// obtain the keyboard value and change to dom.id name
function getKeyValue(value){
    // justify the normal KeyLetter except semicolon
    if(value === "Semicolon"){
        return "Key" + value;
    }
    return value;
}




