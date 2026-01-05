document.addEventListener("DOMContentLoaded", function () {
    let queryEl = document.getElementById("text-box");
    let responseEl = document.getElementById("inside_text");
    let bodyEl = document.getElementById("body");
    let genButton = document.getElementById("gen-button");
    const input = document.getElementById('place_number');

    input.addEventListener('input', () => {
        let value = parseInt(input.value, 10);
        const max_val = parseInt(input.max, 10);
        const min_val = parseInt(input.min, 10);

        if (isNaN(value)) return;
        if (value > max_val) input.value = max_val;
        if (value < min_val) input.value = min_val;
    });

    input.addEventListener('keydown', (e) => {
        if (["Backspace", "ArrowLeft", "ArrowRight", "Delete", "Tab", "Enter"].includes(e.key)) return;
        if (!/^\d$/.test(e.key)) e.preventDefault();
    });

    queryEl.addEventListener("keydown", function (event) {
        if (event.key == "Enter" && !event.shiftKey) {
            event.preventDefault();
            genButton.click();
        }
    });

    window.generateResponse = function () {
        if (queryEl.value.trim() !== "") {
            let query = document.createElement("p");
            query.textContent = queryEl.value;
            query.className = "user-text";
            const ques = queryEl.value;
            queryEl.value = "";
            bodyEl.appendChild(query);

            // let image = document.createElement("img");
            // image.src = "colin-watts-Wr0vLdN3roE-unsplash.jpg";
            // image.className="image_gen"
            // bodyEl.appendChild(image)
            
            let ans = document.createElement("p");
            ans.className = "bot-text";
            ans.textContent = "Working over your query ✅...";
            bodyEl.appendChild(ans);
            bodyEl.scrollTop = bodyEl.scrollHeight;

            setTimeout(() => {
                ans.textContent = "You're into semantic search 🔎...";
            }, 1500);
            setTimeout(() => {
                ans.textContent = "Your chosen k is: " + input.value;
            }, 3000);
            setTimeout(() => {
                ans.textContent = "Analysing the retrieved paragraphs 🕵🏻...";
            }, 4500);
            setTimeout(() => {
                ans.textContent = "Our wizard is casting the ‘load’ spell… please hold your applause.";
            }, 6000);
            setTimeout(() => {
                sendQ(ans, ques, input.value);
            }, 7500);
        }
    }

    function sendQ(ans, ques, k) {
        fetch('http://127.0.0.1:8000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_query: ques, k: Number(k) })
        })
        .then(response => response.json())
        .then(data => {
            ans.textContent = data.reply;
        });
    }
});
