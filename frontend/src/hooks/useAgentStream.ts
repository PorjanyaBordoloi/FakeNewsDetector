import { useState, useCallback } from 'react';

interface AgentThought {
    agent: string;
    status: string;
    thought: string;
    data?: any;
}

/**
 * useAgentStream — SSE hook for agent updates.
 * Connects to the /api/analyze-stream endpoint and receives
 * real-time agent thought events via Server-Sent Events.
 */
export function useAgentStream() {
    const [thoughts, setThoughts] = useState<AgentThought[]>([]);
    const [isComplete, setIsComplete] = useState(false);
    const [finalResult, setFinalResult] = useState<any>(null);

    const startStream = useCallback((url: string) => {
        const eventSource = new EventSource(
            `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/analyze-stream?url=${encodeURIComponent(url)}`
        );

        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.status === 'complete') {
                setIsComplete(true);
                setFinalResult(data);
                eventSource.close();
            } else {
                setThoughts((prev) => [...prev, data]);
            }
        };

        eventSource.onerror = () => {
            eventSource.close();
        };

        return () => eventSource.close();
    }, []);

    const resetStream = useCallback(() => {
        setThoughts([]);
        setIsComplete(false);
        setFinalResult(null);
    }, []);

    return { thoughts, isComplete, finalResult, startStream, resetStream };
}
