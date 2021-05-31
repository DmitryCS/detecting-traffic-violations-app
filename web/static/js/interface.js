globalThis.videos = {'kompol-9s':"./static/raw/blanks/0512_ready.mp4"}
$( "#video-select" ).change(function() {
    $("#video-view").attr("src","");
    setVideoFileUrl();
    if (this.value == "custom") {
        $("#video-form").show();
    }
    else $("#video-form").hide();
    if (this.value == "youtube-link") {
        $("#video-view").hide();
        $("#video-form2").show();
    }
    else {
        $("#video-form2").hide();
        $("#youtube-link").hide();
    }
    if (this.value == "kompol-9s") {
        setVideoFileUrl(globalThis.videos[this.value], "video/mp4");
    }
});
function getId(url) {
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
    const match = url.match(regExp);

    return (match && match[2].length === 11)
      ? match[2]
      : null;
}
$("#but-download").click(function (){
    var youtube_watch_link = document.getElementById("youtube-video").value
    const videoId = getId(youtube_watch_link);
    document.getElementById("youtube-link").src = "https://www.youtube.com/embed/"+videoId;
    $("#youtube-link").show();
});

let STATE = {UPLOAD: 1, PROGRESS: 2, DOWNLOAD: 3};

class InterfaceState {
    constructor(state = null) {
        this.uploadSection = document.getElementById('sendVideoForm');
        this.progressSection = document.getElementById('detectionProccess');
        this.downloadSection = document.getElementById('downloadResult');
        if (state) this.setState(state);
        this.progressUpdateTimerId = null;
    }
    setState(state, processId)
    {
        this.uploadSection.hidden = true;
        this.progressSection.hidden = true;
        this.downloadSection.hidden = true;

        if (state===STATE.UPLOAD) {
            this.uploadSection.hidden = false;
            clearTimeout(this.progressUpdateTimerId);
        }
        else if (state === STATE.PROGRESS) {
            this.progressSection.hidden = false;
        }
        else if (state === STATE.DOWNLOAD) {
            this.downloadSection.hidden = false;
            clearTimeout(this.progressUpdateTimerId);
        }
    }
}

let interfaceState = new InterfaceState(STATE.UPLOAD);


function setVideoFileUrl(url, type, id_video_view = "#video-view") {
    if (url && type) {
        $(id_video_view).show();
        $(id_video_view + ">video").attr("src",url);
        $(id_video_view + ">video").attr("type",type);
        return;
    }
    let file = document.getElementById("video-file").files[0];
    if (file){
        $("#video-view").show();

        let regexp = /mp4$/i;
        if (regexp.test(file.name)) $("#video-view>video").attr("type","video/mp4");
        else $("#video-view>video").attr("type","");

        $(id_video_view + ">video").attr("src",URL.createObjectURL(file));
    }
    else $("#video-view").hide();
}

$("#video-file").change(setVideoFileUrl);
setVideoFileUrl(document.getElementById("youtube-video").value, "video/mp4")

$("#send-video").click(function (){
    let file = document.getElementById("video-file").files[0];
    let youtube_file = document.getElementById("youtube-video").value;
    if (file) {
        var fd = new FormData();
        fd.append('file',file);
        $.ajax({
            type: "POST",
            enctype: 'multipart/form-data',
            url: "http://localhost:8000/file",
            data: fd,
            processData: false,
            contentType: false,
            cache: false,
            success: function (response) {
                console.log(response);
                if(response['existing']){
                    alert("Video existing")
                    return 0;
                }
                interfaceState.setState(STATE.PROGRESS);
                interfaceState.progressUpdateTimerId = setInterval(() => checkProgress(response['progress_id'], response['file_name']),1000);
            },
            error: function (e) {
                console.log("ERROR : ", e);
            }
        });
    }
    else if(youtube_file){
        var youtube_link = {'file':youtube_file};
        $.ajax({
            type: "POST",
            url: "http://localhost:8000/youtube_file",
            data: JSON.stringify(youtube_link),
            success: function (response) {
                console.log(response);
                if(response['existing']){
                    alert("Video existing")
                    return 0;
                }
                interfaceState.setState(STATE.PROGRESS);
                interfaceState.progressUpdateTimerId = setInterval(() => checkProgress(response['progress_id'], response['file_name']),1000);
            },
            error: function (e) {
                console.log("ERROR : ", e);
            }
        });
    }
})

async function checkProgress(processId, file_name)
{
    console.log('check on', processId)

    $.ajax({
        url: 'http://localhost:8000/progress/'+ processId.toString(), //globalThis.progressLink + '/' + processId,
        success: function (data) {
            updateProgressbar(data);
            if (data['progress_percantage'] == 100){
                console.log('FILE IS READY');
                clearInterval(interfaceState.progressUpdateTimerId);
                setVideoFileUrl("/static/raw/"+file_name,"video/mp4", "#video-download");
                interfaceState.setState(STATE.DOWNLOAD);
                $("#video-download>video").attr('src', "/static/raw/"+file_name);
                $("#download-mp4-file").attr('href', "/static/raw/"+file_name);
            }
            else{
                console.log(data['progress_percantage'])
            }

        },
        error: function (error) {
            interfaceState.setState(STATE.UPLOAD)
        }
    })
}

function updateProgressbar(data){
    console.log(data)
    $("#detectionProgressbar").text(data["progress_percantage"].toString() + "%");
}
