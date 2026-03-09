import React from 'react';

interface AgentThought {
    agent: string;
    status: string;
    thought: string;
    data?: any;
}

interface AgentChainProps {
    thoughts: AgentThought[];
    isComplete: boolean;
}

/**
 * AgentChain — Chain of thought display.
 * Shows real-time agent thinking process with status indicators.
 */
const AgentChain: React.FC<AgentChainProps> = ({ thoughts, isComplete }) => {
    const getAgentLabel = (agent: string): string => {
        switch (agent) {
            case 'parser':
                return '🔍 Agent 1: Content Extractor';
            case 'fact_checker':
                return '🔎 Agent 2: Fact Checker';
            case 'cross_reference':
                return '✅ Agent 3: Cross-Reference Validator';
            default:
                return agent;
        }
    };

    const getStatusIcon = (status: string): string => {
        switch (status) {
            case 'started':
                return '⏳';
            case 'progress':
                return '⚙️';
            case 'success':
                return '✅';
            default:
                return '❔';
        }
    };

    return (
        <div className="agent-thinking-container">
            <h2>Agent Analysis Progress</h2>

            {thoughts.map((thought, index) => (
                <div key={index} className={`thought-item agent-${thought.agent}`}>
                    <div className="agent-badge">{getAgentLabel(thought.agent)}</div>
                    <div className="thought-content">
                        <span className={`status-${thought.status}`}>
                            {getStatusIcon(thought.status)}
                        </span>
                        {thought.thought}
                    </div>
                    {thought.data && (
                        <div className="thought-data">
                            {/* Render relevant data preview */}
                        </div>
                    )}
                </div>
            ))}

            {isComplete && (
                <div className="analysis-complete">✅ Analysis Complete!</div>
            )}
        </div>
    );
};

export default AgentChain;
