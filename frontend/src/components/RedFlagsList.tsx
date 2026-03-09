import React from 'react';

interface RedFlag {
    type: string;
    description: string;
    severity: string;
}

interface RedFlagsListProps {
    redFlags: RedFlag[];
}

/**
 * RedFlagsList — Red flags breakdown.
 * Displays identified issues with severity levels.
 */
const RedFlagsList: React.FC<RedFlagsListProps> = ({ redFlags }) => {
    const getSeverityIcon = (severity: string): string => {
        switch (severity) {
            case 'critical':
                return '🔴';
            case 'high':
                return '🟠';
            case 'medium':
                return '🟡';
            case 'low':
                return '🟢';
            default:
                return '⚪';
        }
    };

    if (redFlags.length === 0) {
        return null;
    }

    return (
        <div className="red-flags-list">
            <h3>🚩 Red Flags</h3>
            <ul>
                {redFlags.map((flag, index) => (
                    <li key={index} className={`red-flag severity-${flag.severity}`}>
                        <span className="severity-icon">{getSeverityIcon(flag.severity)}</span>
                        <span className="flag-type">{flag.type.replace(/_/g, ' ')}</span>
                        <p className="flag-description">{flag.description}</p>
                        <span className="flag-severity">{flag.severity.toUpperCase()}</span>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default RedFlagsList;
