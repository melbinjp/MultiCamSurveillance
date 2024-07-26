document.addEventListener('DOMContentLoaded', function() {
    const video = document.getElementById('video-feed');
    const source = new EventSource('/video_feed/0'); // Adjust the camera ID as needed

    source.onmessage = function(event) {
        video.src = 'data:image/jpeg;base64,' + event.data;
    };
});
