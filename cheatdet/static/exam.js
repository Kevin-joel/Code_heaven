const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const statusDiv = document.getElementById("status");

navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(err => {
        alert("Camera access denied!");
    });

function captureFrame() {
    const context = canvas.getContext("2d");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0);
    return canvas.toDataURL("image/jpeg");
}

function sendFrame() {
    const image = captureFrame();

    fetch("/detect", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: image })
    })
    .then(res => res.json())
    .then(data => {

        if (data.status === "Warning") {
            statusDiv.innerHTML = `⚠ Warning (${data.warnings}/2): ${data.reason}`;
            statusDiv.className = "status warning";
        }

        else if (data.status === "Terminate") {
            statusDiv.innerHTML = `❌ Exam Terminated: ${data.reason}`;
            statusDiv.className = "status terminate";
            setTimeout(() => window.location.href = "/logout", 3000);
        }

        else {
            statusDiv.innerHTML = "Monitoring...";
            statusDiv.className = "status normal";
        }
    });
}

setInterval(sendFrame, 2000);

// Tab switch detection
document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
        alert("Tab switching detected!");
    }
});
