document.addEventListener('DOMContentLoaded', () => {
    const audioFile = document.getElementById('audioFile');
    const imageFile = document.getElementById('imageFile');
    const uploadAudioBtn = document.getElementById('uploadAudio');
    const uploadImageBtn = document.getElementById('uploadImage');
    const createVideoBtn = document.getElementById('createVideo');
    const cancelVideoBtn = document.getElementById('cancelVideo');
    const downloadLink = document.getElementById('downloadLink');
    const audioMessage = document.getElementById('audioMessage');
    const imageMessage = document.getElementById('imageMessage');
    const videoMessage = document.getElementById('videoMessage');
    const selectedAudioFile = document.getElementById('selectedAudioFile');
    const selectedImageFile = document.getElementById('selectedImageFile');
    const audioUploadIndicator = document.getElementById('audioUploadIndicator');
    const imageUploadIndicator = document.getElementById('imageUploadIndicator');
    const progressBarContainer = document.getElementById('progressBarContainer');
    const progressBar = document.getElementById('progressBar');
    const audioLoadingSpinner = document.getElementById('audioLoadingSpinner');
    const resolutionSelect = document.getElementById('resolution');
    const qualitySelect = document.getElementById('quality');
    const audioFileSelect = document.getElementById('audioFileSelect');
    const imageFileSelect = document.getElementById('imageFileSelect');
    const videoFileSelect = document.getElementById('videoFileSelect');

    let audioPath = null;
    let imagePath = null;
    let eventSource;
    let cancelVideoCreation = false;

    function updateUploadIndicator(indicator, success) {
        indicator.textContent = success ? '✓' : '✗';
        indicator.style.color = success ? 'green' : 'red';
        indicator.style.opacity = '0';
        setTimeout(() => {
            indicator.style.transition = 'opacity 0.5s ease-in-out';
            indicator.style.opacity = '1';
        }, 10);
    }

    function showMessage(element, message, color = 'black') {
        element.textContent = message;
        element.style.color = color;
        element.style.opacity = '0';
        setTimeout(() => {
            element.style.transition = 'opacity 0.5s ease-in-out';
            element.style.opacity = '1';
        }, 10);
    }

    function showError(element, message) {
        showMessage(element, message, 'red');
    }

    function showSuccess(element, message) {
        showMessage(element, message, 'green');
    }

    function fetchUploadedFiles() {
        fetch('/list_audio_files')
            .then(response => response.json())
            .then(data => {
                audioFileSelect.innerHTML = '<option value="">Select an audio file</option>';
                data.forEach(file => {
                    const option = document.createElement('option');
                    option.value = file;
                    option.textContent = file;
                    audioFileSelect.appendChild(option);
                });
            });

        fetch('/list_image_files')
            .then(response => response.json())
            .then(data => {
                imageFileSelect.innerHTML = '<option value="">Select an image file</option>';
                data.forEach(file => {
                    const option = document.createElement('option');
                    option.value = file;
                    option.textContent = file;
                    imageFileSelect.appendChild(option);
                });
            });

        fetch('/list_video_files')
            .then(response => response.json())
            .then(data => {
                videoFileSelect.innerHTML = '<option value="">Select a video file</option>';
                data.forEach(file => {
                    const option = document.createElement('option');
                    option.value = file;
                    option.textContent = file;
                    videoFileSelect.appendChild(option);
                });
            });
    }

    fetchUploadedFiles();

    audioFile.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            if (file.size > 5 * 1024 * 1024) {
                showError(audioMessage, 'File size exceeds the limit of 5MB');
                audioFile.value = '';
                selectedAudioFile.textContent = '';
                uploadAudioBtn.disabled = true;
            } else {
                selectedAudioFile.textContent = file.name;
                uploadAudioBtn.disabled = false;
            }
        } else {
            selectedAudioFile.textContent = '';
            uploadAudioBtn.disabled = true;
        }
        audioUploadIndicator.textContent = '';
    });

    imageFile.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            selectedImageFile.textContent = file.name;
            uploadImageBtn.disabled = false;
        } else {
            selectedImageFile.textContent = '';
            uploadImageBtn.disabled = true;
        }
        imageUploadIndicator.textContent = '';
    });

    uploadAudioBtn.addEventListener('click', () => {
        if (!audioFile.files[0]) {
            showError(audioMessage, 'Please select an audio file first.');
            return;
        }

        const formData = new FormData();
        formData.append('audio', audioFile.files[0]);

        showMessage(audioMessage, 'Uploading audio...');
        audioLoadingSpinner.style.display = 'inline-block';
        uploadAudioBtn.disabled = true;

        fetch('/upload_audio', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            audioLoadingSpinner.style.display = 'none';
            uploadAudioBtn.disabled = false;
            if (data.error) {
                showError(audioMessage, data.error);
                updateUploadIndicator(audioUploadIndicator, false);
            } else {
                showSuccess(audioMessage, data.message);
                updateUploadIndicator(audioUploadIndicator, true);
                audioPath = data.path;
                checkCreateVideoEnabled();
                fetchUploadedFiles();
            }
        })
        .catch(error => {
            audioLoadingSpinner.style.display = 'none';
            uploadAudioBtn.disabled = false;
            showError(audioMessage, 'Error uploading audio: ' + error);
            updateUploadIndicator(audioUploadIndicator, false);
        });
    });

    uploadImageBtn.addEventListener('click', () => {
        if (!imageFile.files[0]) {
            showError(imageMessage, 'Please select an image file first.');
            return;
        }

        const formData = new FormData();
        formData.append('image', imageFile.files[0]);

        showMessage(imageMessage, 'Uploading image...');
        fetch('/upload_image', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showError(imageMessage, data.error);
                updateUploadIndicator(imageUploadIndicator, false);
            } else {
                showSuccess(imageMessage, data.message);
                updateUploadIndicator(imageUploadIndicator, true);
                imagePath = data.path;
                checkCreateVideoEnabled();
                fetchUploadedFiles();
            }
        })
        .catch(error => {
            showError(imageMessage, 'Error uploading image: ' + error);
            updateUploadIndicator(imageUploadIndicator, false);
        });
    });

    createVideoBtn.addEventListener('click', () => {
        showMessage(videoMessage, 'Creating video...');
        progressBarContainer.style.display = 'block';
        progressBar.style.width = '0%';
        createVideoBtn.style.display = 'none';
        cancelVideoBtn.style.display = 'inline-block';
        cancelVideoCreation = false;

        console.log('Starting video creation process');

        fetch('/create_video', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                audio_filename: audioPath.split('/').pop(),
                image_filename: imagePath.split('/').pop(),
                resolution: resolutionSelect.value,
                quality: qualitySelect.value
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Video creation started:', data);
            connectEventSource();
        })
        .catch(error => {
            console.error('Fetch error:', error);
            showError(videoMessage, `Error sending video creation request: ${error.message}`);
            createVideoBtn.style.display = 'inline-block';
            cancelVideoBtn.style.display = 'none';
        });
    });

    cancelVideoBtn.addEventListener('click', () => {
        if (eventSource) {
            console.log('Cancelling video creation');
            eventSource.close();
            cancelVideoCreation = true;
            showMessage(videoMessage, 'Video creation cancelled', 'orange');
            createVideoBtn.style.display = 'inline-block';
            cancelVideoBtn.style.display = 'none';
        }
    });

    function connectEventSource() {
        console.log('Connecting to EventSource');
        if (eventSource) {
            console.log('Closing existing EventSource connection');
            eventSource.close();
        }
        eventSource = new EventSource('/create_video');

        eventSource.onopen = (event) => {
            console.log('EventSource connection opened', event);
        };

        eventSource.onmessage = (event) => {
            console.log('Received SSE message:', event.data);
            try {
                const data = JSON.parse(event.data);
                if (data.progress) {
                    console.log(`Video creation progress: ${data.progress}%`);
                    progressBar.style.width = `${data.progress}%`;
                } else if (data.message) {
                    console.log('Video creation completed:', data.message);
                    showSuccess(videoMessage, data.message);
                    if (data.video_path) {
                        downloadLink.href = `/download_video/${data.video_path}`;
                        document.querySelector('.download-section').style.display = 'block';
                    }
                    eventSource.close();
                    createVideoBtn.style.display = 'inline-block';
                    cancelVideoBtn.style.display = 'none';
                    fetchUploadedFiles();
                } else if (data.error) {
                    console.error('Error creating video:', data.error);
                    showError(videoMessage, `Error creating video: ${data.error}`);
                    eventSource.close();
                    createVideoBtn.style.display = 'inline-block';
                    cancelVideoBtn.style.display = 'none';
                }
            } catch (error) {
                console.error('Error parsing SSE message:', error);
                showError(videoMessage, 'Error processing server response');
                eventSource.close();
                createVideoBtn.style.display = 'inline-block';
                cancelVideoBtn.style.display = 'none';
            }
        };

        eventSource.onerror = (error) => {
            console.error('SSE error:', error);
            eventSource.close();
            showError(videoMessage, 'Error connecting to server. Attempting to reconnect...');
            setTimeout(() => {
                console.log('Attempting to reconnect...');
                connectEventSource();
            }, 5000);
        };
    }

    function checkCreateVideoEnabled() {
        createVideoBtn.disabled = !(audioPath && imagePath);
    }

    audioFileSelect.addEventListener('change', function() {
        if (this.value) {
            audioPath = '/uploads/audio/' + this.value;
            showSuccess(audioMessage, 'Selected audio file: ' + this.value);
            checkCreateVideoEnabled();
        }
    });

    imageFileSelect.addEventListener('change', function() {
        if (this.value) {
            imagePath = '/uploads/images/' + this.value;
            showSuccess(imageMessage, 'Selected image file: ' + this.value);
            checkCreateVideoEnabled();
        }
    });

    videoFileSelect.addEventListener('change', function() {
        if (this.value) {
            const downloadLink = document.getElementById('downloadLink');
            downloadLink.href = '/download_video/' + this.value;
            document.querySelector('.download-section').style.display = 'block';
            showSuccess(videoMessage, 'Selected video file: ' + this.value);
        }
    });
});