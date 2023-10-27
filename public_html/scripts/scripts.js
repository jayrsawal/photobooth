const giphyApiKey = "qeib1DCrfj547lTtvr65BiS3Z6JhdgkP"

// Grab elements, create settings, etc.
var video = document.getElementById('video');
var config = { 
    video: {
        width: {
            min: 1280,
            ideal: 2160,
            max: 2160
        },
        height: {
            min: 720,
            ideal: 2160,
            max: 2160
        }
    },
    audio: false
}

// Get access to the camera!
if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    // Not adding `{ audio: true }` since we only want video now
    navigator.mediaDevices.getUserMedia(config).then(function(stream) {
        //video.src = window.URL.createObjectURL(stream);
        video.srcObject = stream;
        video.play();
    });
}

// Trigger photo take
document.getElementById("control-three").addEventListener("click", function() {
    resetStage();
    triggerPhoto(3, Date.now().toString(), 1, "GET READY", second);
});

document.getElementById("control-one").addEventListener("click", function() {
    resetStage();
    triggerPhoto(3, Date.now().toString(), 1, "GET READY", save);
});

// document.getElementById("control-two").addEventListener("click", function() {
//     resetStage();
//     triggerPhoto(3, Date.now().toString(), 1, "GET READY", third);
// });


document.getElementById("collage").addEventListener("mouseover", function() {
    document.getElementById("collage").classList.add("zoom");
});

document.getElementById("collage").addEventListener("mouseout", function() {
    document.getElementById("collage").classList.remove("zoom");
});

function second(groupId) {
    setTimeout(function() {
        triggerPhoto(3, groupId, 2, "LOOK HERE", third)
    }, 5 * 1000);
}

function third(groupId) {
    setTimeout(
        function() {
            triggerPhoto(3, groupId, 3, "LAST ONE", save);
        }
    , 5 * 1000)
}

function save(groupId) {
    setTimeout(function() {
        snack("NICE")
        eatSnack(2)
    }, 1000)

    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState == XMLHttpRequest.DONE) {
            document.getElementById("collage").setAttribute("src", "");
            data = JSON.parse(xhr.responseText)
            document.getElementById("collage").setAttribute("src", data["photo_url"]);
            document.getElementById("output").classList.remove("hide");
        }
    }

    xhr.open("GET", "/upload/"+groupId, true);
    xhr.send();

	document.getElementById("control-one").classList.remove("hide")
    // document.getElementById("control-two").classList.remove("hide")
    document.getElementById("control-three").classList.remove("hide")
}

function triggerPhoto(seconds, groupId, photoNum, message, callback) {
	document.getElementById("overlay").classList.remove("hide")
    var tick = document.getElementById("audio-tick");
    tick.play()

    var chime = document.getElementById("audio-chime");
    chime.play()

	snack(message)
    setTimeout(countDown, 1 * 1000, groupId, seconds, photoNum, callback)
}

function countDown(groupId, seconds, photoNum, callback) {
	document.getElementById("overlay").classList.add("hide")
    
    let count = seconds
    for(i=1; i <= seconds; i++) {
        setTimeout(function(x) {
            var beep = document.getElementById("audio-beep");
            beep.play()
            snack(x)
        }, i * 1000, count);
        count--;
    }

    setTimeout(takePhoto, (seconds+1) * 1000, groupId, photoNum, callback);
}

function takePhoto(groupId, photoNum, callback) {
    // var canvas = document.getElementById('canvas');
    // var context = canvas.getContext('2d');
    // var video = document.getElementById('video');
    // canvas.height = video.offsetHeight;
    // canvas.width = video.offsetWidth;
    // context.drawImage(video, 0, 0, video.offsetWidth, video.offsetHeight);
    
	document.getElementById("control-one").classList.add("hide");
    // document.getElementById("control-two").classList.add("hide");
    document.getElementById("control-three").classList.add("hide");

    // const data = canvas.toDataURL("image/png");
    getPhoto(groupId, photoNum, (gid) => {
        shutter();
        callback(gid);
    });
    eatSnack(0);
}

function resetStage() {
    for (i = 1; i<=3; i++) {
        document.getElementById("photo"+i).classList.add("hide");
        document.getElementById("photo"+i).setAttribute("src", "");
    }
    document.getElementById("output").classList.add("hide");
    document.getElementById("gallery").classList.add("hide")
	document.getElementById("control-one").classList.add("hide")
    // document.getElementById("control-two").classList.add("hide")
    document.getElementById("control-three").classList.add("hide")
}

function snack(txt) {
    document.getElementById('banner').classList.remove("hidden")
    document.getElementById("banner-text").textContent = txt;
}

function eatSnack(delay) {
    if (delay == 0) {
        document.getElementById('banner').classList.add("hidden")
    }
    setTimeout(function() {
        document.getElementById('banner').classList.add("hidden")
    }, delay * 1000)
}

function shutter() {
    var shutter = document.getElementById("audio-shutter");
    shutter.play()
    var tick = document.getElementById("audio-tick");
    tick.pause()
    tick.currentTime = 0;

    document.getElementById('shutter').classList.remove("hide")
    document.getElementById('shutter').classList.remove("hidden")
    setTimeout(function() {
        document.getElementById('shutter').classList.add("hidden")
    }, 200)
    setTimeout(function() {
        document.getElementById('shutter').classList.add("hide")
    }, 2000)
}

function getPhoto(groupId, photoNum, callback) {
    var photoId = "photo" + photoNum;

    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState == XMLHttpRequest.DONE) {
            document.getElementById("gallery").classList.remove("hide");
            document.getElementById("gallery").classList.remove("hidden");

            document.getElementById(photoId).classList.remove("hide");
            document.getElementById(photoId).classList.remove("hidden");
            setTimeout(function() {
                document.getElementById("gallery").classList.add("hidden");
                setTimeout(function() {
                    document.getElementById("gallery").classList.add("hide");
                }, 1000);
            }, 5000);

            document.getElementById(photoId).setAttribute("src", xhr.response);
            
            getGif("nice+photo");
            callback(groupId);
        }
    }
    xhr.open("GET", "/photo/" + groupId + "/" + photoNum, true);
    xhr.send()
}

function getGif(message) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState == XMLHttpRequest.DONE) {
            var gifUrl = JSON.parse(xhr.response)["data"][0]["images"]["original"]["url"];
            var cheer = document.getElementById("nice")
            cheer.setAttribute("src", gifUrl);
            setTimeout(
                function() {
                    document.getElementById("cheer").classList.remove("hide");
                    setTimeout(function() {
                        document.getElementById("cheer").classList.add("hide")
                    }, 3000);
                }
            , 1000)
        }
    }
    xhr.open("GET", "http://api.giphy.com/v1/gifs/search?q=" + message + "&api_key=" + giphyApiKey + "&limit=1&offset=" + (Math.floor(Math.random() * 100)), true);
    xhr.send()
}
