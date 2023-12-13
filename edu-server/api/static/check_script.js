function checkVideo() {
    const videoId = document.getElementById('videoId').value;

    // Assume you have an API endpoint for video checking
    const apiUrl = '/api/predict';

    // Make a POST request to the backend API
    fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ videoId: videoId }),
    })
    .then(response => response.json())
    .then(data => {
        // Display the result to the user
        const resultElement = document.getElementById('result');
        console.log(data)
        if (data.response) {
            resultElement.textContent = 'Educational!';
            resultElement.style.color = 'green';
        } else {
            resultElement.textContent = 'Not Educational!';
            resultElement.style.color = 'red';
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
