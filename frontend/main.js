document.getElementById("submitBtn").addEventListener("click", function() {
    const query = document.getElementById("query").value;
    const loadingDiv = document.getElementById("loading");
    const resultDiv = document.getElementById("result");
    loadingDiv.style.display = "block";
    resultDiv.style.display = "none";
    
    // Make a POST request to the backend API with the query
    fetch("http://127.0.0.1:5000/api/query", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ query: query })
    })
    .then(response => response.json())
    .then(data => {
        loadingDiv.style.display = "none";
        resultDiv.style.display = "block";
        resultDiv.innerHTML = data.insight || data.error;
        handleResponse(data);
    })
    .catch(error => {
        loadingDiv.style.display = "none";
        resultDiv.style.display = "block";
        resultDiv.innerText = "Error: " + error;
    });
});

document.getElementById("compareBtn").addEventListener("click", function() {
    const loadingDiv = document.getElementById("loading");
    const resultDiv = document.getElementById("result");
    loadingDiv.style.display = "block";
    resultDiv.style.display = "none";
    
    // Optionally, pass report identifiers if needed
    fetch("http://127.0.0.1:5000/api/compare", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ report1: "Report1", report2: "Report2" })
    })
    .then(response => response.json())
    .then(data => {
        loadingDiv.style.display = "none";
        resultDiv.style.display = "block";
        resultDiv.innerHTML = data.comparison || data.error;
        handleResponse(data);
    })
    .catch(error => {
        loadingDiv.style.display = "none";
        resultDiv.style.display = "block";
        resultDiv.innerText = "Error: " + error;
    });
});

// Function to handle the response from the backend
function handleResponse(response) {
    // Display sentiment analysis
    const sentimentContainer = document.getElementById('sentiment');
    sentimentContainer.innerHTML = `<h3>Sentiment Analysis</h3><pre>${JSON.stringify(response.sentiment, null, 2)}</pre>`;

    // Display topic modeling
    const topicsContainer = document.getElementById('topics');
    topicsContainer.innerHTML = `<h3>Topic Modeling</h3><pre>${JSON.stringify(response.topics, null, 2)}</pre>`;

    // Display sources with links
    const sourceListDiv = document.getElementById("sourceList");
    if (response.sources && response.sources.length > 0) {
        sourceListDiv.style.display = "block";
        sourceListDiv.innerHTML = "<strong>Sources:</strong><ul>" +
            response.sources.map((src, index) => `<li><a href="path/to/pdf#page=${index + 1}" target="_blank">${src}</a></li>`).join("") + "</ul>";
    } else {
        sourceListDiv.style.display = "block";
        sourceListDiv.innerHTML = "<strong>Sources:</strong> No source sentences provided.";
    }
}
