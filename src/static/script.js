document.getElementById('uploadForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
   
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    const endpoint = file.type.startsWith('image/') ? '/detect/' : '/detect-video/';
   
    // Clear previous results and show loading animation
    const resultContainer = document.getElementById('result');
    resultContainer.innerHTML = '';
   
    const loadingSpinner = document.getElementById('loading');
    loadingSpinner.style.display = 'block';
   
    try {
        const startTime = performance.now();
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });

        const endTime = performance.now();
        const totalResponseTime = ((endTime - startTime) / 1000).toFixed(2); // Convert to seconds
       
        if (!response.ok) throw new Error('Failed to process file');

        // Get prediction time from response headers
        const predictionTime = response.headers.get("X-Prediction-Time");

        // Create a blob URL for the file
        const blobUrl = URL.createObjectURL(await response.blob());
       
        // Hide loading animation
        loadingSpinner.style.display = 'none';

        // Display statistics
        const statsDiv = document.createElement('div');
        statsDiv.className = 'statistics';

        const processingTimeDiv = document.createElement('div');
        processingTimeDiv.innerHTML = `<p><strong>Processing Time:</strong> ${parseFloat(predictionTime).toFixed(2)}s</p>`;

        const totalResponseTimeDiv = document.createElement('div');
        totalResponseTimeDiv.innerHTML = `<p><strong>Total Response Time:</strong> ${totalResponseTime}s</p>`;

        statsDiv.appendChild(processingTimeDiv);
        statsDiv.appendChild(totalResponseTimeDiv);

        resultContainer.appendChild(statsDiv);

        // Display media
        const mediaDiv = document.createElement('div');
        mediaDiv.className = 'media-display';

        if (file.type.startsWith('image/')) {
            // Display image
            const imgElement = document.createElement('img');
            imgElement.src = blobUrl;
            imgElement.alt = 'Processed Image';
            imgElement.style.maxWidth = '100%';
            mediaDiv.appendChild(imgElement);
           
            // Add download button for image
            const downloadLink = document.createElement('a');
            downloadLink.href = blobUrl;
            downloadLink.download = 'processed_image.jpg';
            downloadLink.textContent = 'Download Image';
            downloadLink.className = 'download-link';
           
            mediaDiv.appendChild(downloadLink);
           
        } else if (file.type.startsWith('video/')) {
            // Display video
            const videoElement = document.createElement('video');
            videoElement.src = blobUrl;
            videoElement.controls = true;
            videoElement.style.maxWidth = '100%';
            mediaDiv.appendChild(videoElement);

            // Add download button for video
            const downloadLink = document.createElement('a');
            downloadLink.href = blobUrl;
            downloadLink.download = 'processed_video.mp4';
            downloadLink.textContent = 'Download Video';
            downloadLink.className = 'download-link';

            mediaDiv.appendChild(downloadLink);
        }

        resultContainer.appendChild(mediaDiv);
       
    } catch (error) {
        console.error(error);
        alert('An error occurred while processing the file.');
       
        // Hide loading animation
        loadingSpinner.style.display = 'none';
    }
});