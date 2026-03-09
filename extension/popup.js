/**
 * popup.js — Extension popup script.
 *
 * Gets the current tab URL, sends it to the /api/analyze-simple endpoint,
 * and displays the score + verdict.
 *
 * Extension displays ONLY:
 *   - Score (0-100)
 *   - Verdict (Fake/Real/Misleading)
 *   - Button to "View Full Analysis" (opens website)
 */

const API_URL = 'http://localhost:8000';

document.getElementById('analyze-btn').addEventListener('click', async () => {
    // Get current tab URL
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const url = tab.url;

    if (!url || url.startsWith('chrome://')) {
        return;
    }

    // Show loading
    document.getElementById('not-article').classList.add('hidden');
    document.getElementById('loading').classList.remove('hidden');

    try {
        const response = await fetch(`${API_URL}/api/analyze-simple?url=${encodeURIComponent(url)}`, {
            method: 'POST',
        });

        const data = await response.json();

        // Hide loading, show result
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('result').classList.remove('hidden');

        // Populate verdict
        const container = document.getElementById('verdict-container');
        const scoreBadge = document.getElementById('score-badge');
        const verdictText = document.getElementById('verdict-text');
        const verdictDesc = document.getElementById('verdict-description');

        scoreBadge.textContent = `Score: ${data.score}/100`;

        if (data.verdict === 'FAKE') {
            container.className = 'verdict verdict-fake';
            verdictText.textContent = '⚠️ Likely Fake';
            verdictDesc.textContent = 'Multiple red flags detected';
        } else if (data.verdict === 'REAL') {
            container.className = 'verdict verdict-real';
            verdictText.textContent = '✅ Likely Real';
            verdictDesc.textContent = 'Verified by trusted sources';
        } else if (data.verdict === 'MISLEADING') {
            container.className = 'verdict verdict-misleading';
            verdictText.textContent = '⚠️ Misleading';
            verdictDesc.textContent = 'Contains some inaccuracies';
        } else {
            container.className = 'verdict';
            verdictText.textContent = '❔ Unverified';
            verdictDesc.textContent = 'Could not be fully verified';
        }
    } catch (error) {
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('not-article').classList.remove('hidden');
        console.error('Analysis failed:', error);
    }
});

// View Full Analysis button → opens website
document.getElementById('view-details')?.addEventListener('click', async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const url = tab.url;
    chrome.tabs.create({ url: `http://localhost:5173?url=${encodeURIComponent(url)}` });
});
