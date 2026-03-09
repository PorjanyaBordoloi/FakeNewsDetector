import React, { useState } from 'react';

interface URLInputProps {
    onSubmit: (url: string) => void;
    isLoading: boolean;
}

/**
 * URLInput — URL submission form.
 * Accepts a news article URL and triggers the analysis pipeline.
 */
const URLInput: React.FC<URLInputProps> = ({ onSubmit, isLoading }) => {
    const [url, setUrl] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (url.trim()) {
            onSubmit(url.trim());
        }
    };

    return (
        <form className="url-input-form" onSubmit={handleSubmit}>
            <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Paste a news article URL to analyze..."
                required
                disabled={isLoading}
            />
            <button type="submit" disabled={isLoading || !url.trim()}>
                {isLoading ? 'Analyzing...' : 'Analyze'}
            </button>
        </form>
    );
};

export default URLInput;
