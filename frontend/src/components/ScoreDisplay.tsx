import React from 'react';

interface ScoreDisplayProps {
    score: number;
    verdict: string;
    confidence: string;
}

/**
 * ScoreDisplay — Final score visualization.
 * Shows the authenticity score (0-100), verdict, and confidence level.
 */
const ScoreDisplay: React.FC<ScoreDisplayProps> = ({ score, verdict, confidence }) => {
    const getVerdictColor = (verdict: string): string => {
        switch (verdict) {
            case 'REAL':
                return 'verdict-real';
            case 'FAKE':
                return 'verdict-fake';
            case 'MISLEADING':
                return 'verdict-misleading';
            default:
                return 'verdict-unverified';
        }
    };

    return (
        <div className={`score-display ${getVerdictColor(verdict)}`}>
            <div className="score-badge">Score: {score}/100</div>
            <h2 className="verdict-label">{verdict}</h2>
            <p className="confidence-label">Confidence: {confidence}</p>
        </div>
    );
};

export default ScoreDisplay;
