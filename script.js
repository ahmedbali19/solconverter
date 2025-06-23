let mediaRecorder;
let recordedChunks = [];

const recordBtn = document.getElementById('recordBtn');
const stopBtn = document.getElementById('stopBtn');
const uploadBtn = document.getElementById('uploadBtn');
const fileInput = document.getElementById('fileInput');
const output = document.getElementById('output');

recordBtn.onclick = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    recordedChunks = [];
    mediaRecorder.ondataavailable = e => {
        if (e.data.size > 0) recordedChunks.push(e.data);
    };
    mediaRecorder.onstop = () => {
        stream.getTracks().forEach(t => t.stop());
    };
    mediaRecorder.start();
    recordBtn.disabled = true;
    stopBtn.disabled = false;
};

stopBtn.onclick = () => {
    mediaRecorder.stop();
    recordBtn.disabled = false;
    stopBtn.disabled = true;
};

uploadBtn.onclick = async () => {
    let blob;
    if (recordedChunks.length) {
        blob = new Blob(recordedChunks, { type: 'audio/mpeg' });
    } else if (fileInput.files[0]) {
        blob = fileInput.files[0];
    } else {
        alert('No file or recording.');
        return;
    }

    const formData = new FormData();
    formData.append('file', blob, 'audio.mp3');

    output.textContent = 'Uploading...';

    try {
        const resp = await fetch('/transcribe/', {
            method: 'POST',
            body: formData
        });
        if (!resp.ok) {
            throw new Error(await resp.text());
        }
        const data = await resp.json();
        output.textContent = data.notation;
    } catch (err) {
        output.textContent = err;
    }
};
