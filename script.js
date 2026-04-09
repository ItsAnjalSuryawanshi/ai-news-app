console.log("JS Loaded");

// Typewriter Effect

function typeWriter(elementId, text, speed = 15) {
    const element = document.getElementById(elementId);
    element.innerHTML = "";

    let i = 0;

    function typing() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            setTimeout(typing, speed);
        }
    }

    typing();
}

// UI State Handlers
function setLoading(isLoading) {
    const status = document.getElementById("status");
    const videoBox = document.getElementById("videoBox");

    if (isLoading) {
        status.innerText = "Analyzing news...";
        videoBox.innerText = "Processing...";
    } else {
        videoBox.innerText = "";
    }
}

function setError(message) {
    document.getElementById("status").innerText = message;
    document.getElementById("videoBox").innerText = "Failed";
}


// API CALL
async function analyzeNews() {

    const url = document.getElementById("url").value.trim();
    const domain = document.getElementById("domain").value;

    if (!url) {
        alert("Please enter a news URL!");
        return;
    }

    setLoading(true);

    try {
        const response = await fetch("http://127.0.0.1:5000/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ url, domain })
        });

        if (!response.ok) {
            throw new Error("Server error");
        }

        const data = await response.json();

        
        // Safe data handling
       
        const summaryText =
            (data.summary || "") +
            "\n\nImportance Score: " + (data.score || 0);

        const highlightsText =
            (data.highlights || "") +
            "\n\nKeywords: " + ((data.keywords || []).join(", "));

        const explanationText =
            (data.hindi || "") +
            "\n\nSentiment: " + (data.sentiment || "Unknown");

       
        // Render UI
        
        typeWriter("summary", summaryText);
        typeWriter("highlights", highlightsText);
        typeWriter("explanation", explanationText);

        document.getElementById("status").innerText = "Analysis complete";

        
        // Speech Output
       
        const speechText = `
            ${data.summary || ""}.
            ${data.highlights || ""}.
            ${data.hindi || ""}
        `;

        const speech = new SpeechSynthesisUtterance(speechText);

        speech.onstart = () => {
            document.getElementById("videoBox").innerText = "Speaking...";
        };

        speech.onend = () => {
            document.getElementById("videoBox").innerText = "Completed";
        };

        speechSynthesis.speak(speech);

    } catch (error) {
        console.error("Error:", error);
        setError("Failed to fetch data. Check backend connection.");
    } finally {
        setLoading(false);
    }
}