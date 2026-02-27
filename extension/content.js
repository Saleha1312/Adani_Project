(async function () {
    try {
        // 1. Extract Data from DOM
        const url = window.location.href;
        const title = document.title;

        // Extract headings (h1, h2, h3)
        const headings = Array.from(document.querySelectorAll('h1, h2, h3'))
            .map(h => h.innerText.trim())
            .filter(text => text.length > 0);

        // Deep clone the body so we can modify it without breaking the live page
        const clonedBody = document.body.cloneNode(true);

        // Remove unwanted elements: nav, footer, header, scripts, styles, links
        const elementsToRemove = clonedBody.querySelectorAll('nav, footer, header, script, style, a, noscript, iframe');
        elementsToRemove.forEach(el => el.remove());

        // Extract the remaining text content, split by newlines, and clean up
        let rawText = clonedBody.innerText || clonedBody.textContent;
        let contentArray = rawText.split('\n')
            .map(text => text.replace(/\s+/g, ' ').trim())
            .filter(text => text.length > 0);

        // Prepare payload to match our Pydantic schema
        const payload = {
            url: url,
            title: title,
            headings: headings,
            content: contentArray
        };

        // 2. Send to Backend API
        // Make sure the FastAPI server is running on localhost:8000
        const response = await fetch('http://localhost:8000/api/data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Server error: ${response.status}`);
        }

        const data = await response.json();

        // Return success object back to popup.js
        return { success: true, id: data.inserted_id };

    } catch (error) {
        console.error("Scraper Error:", error);
        // Sometimes Error objects don't serialize well over chrome channels, so send message
        return { success: false, error: error.message || String(error) };
    }
})();
