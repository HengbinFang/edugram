

var videos = []

async function GetVidData() {
  const request = await fetch("/api/get_reel");
  const data = await request.json()
  console.log(data)
  for (let i = 0; i < data.length; i++) {
    videos.push(data[i])
  }
}

GetVidData()
console.log(videos)

// Function to make the API request
function fetchReels(reelsId) {
  // Replace 'your-api-endpoint' with the actual URL of the API
  const apiUrl = "/api/get_embed?id=" + reelsId;

  // Making the Fetch request
  return fetch(apiUrl)
    .then(response => {
      // Check if the request was successful
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      // Parse the response as JSON
      return response.json();
    })
    .catch(error => {
      // Handle errors here
      console.error('Error:', error);
      throw error; // Optional: rethrow the error to propagate it further
    });
}

async function ChangeIt() {
    const reelsContainer = document.getElementById('reels-box');
    // Example of using the fetchData function
    fetchReels(videos.pop(0)).then(data => {
      reelsContainer.srcdoc  = data.html
      console.log(reelsContainer)
      reelsContainer.style = "width: 325px; height: 650px; overflow: hidden; border-radius: 50px; margin-top: 20px"
      const scripts = reelsContainer.getElementsByTagName('script');
      console.log(scripts)

      for (let i = 0; i < scripts.length; i++) {
        const script = scripts[i];
        const newScript = document.createElement('script');
        newScript.src = script.src;
        newScript.innerHTML = script.innerHTML;
        script.parentNode.replaceChild(newScript, script);
      }
      if (videos.length == 0) {
        GetVidData()
      }
    })
    .catch(error => {
      console.error('Error:', error);
    });
    
  }


