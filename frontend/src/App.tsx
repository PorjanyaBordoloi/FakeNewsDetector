import React, { useState } from 'react';
import URLInput from './components/URLInput';
import AgentChain from './components/AgentChain';
import ScoreDisplay from './components/ScoreDisplay';
import RedFlagsList from './components/RedFlagsList';
import SourceCitations from './components/SourceCitations';
import ExportReport from './components/ExportReport';
import { useAgentStream } from './hooks/useAgentStream';
import { useAnalysis } from './hooks/useAnalysis';

function App() {
    const [url, setUrl] = useState<string>('');
    const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);

    const { thoughts, isComplete, finalResult, startStream, resetStream } = useAgentStream();
    const { analysisData, setAnalysisData } = useAnalysis();

    const handleSubmit = async (submittedUrl: string) => {
        setUrl(submittedUrl);
        setIsAnalyzing(true);
        resetStream();
        startStream(submittedUrl);
    };

    return (
        <div className="app">
            <header className="app-header">
                <h1>🔍 Fake News Detector</h1>
                <p>AI-Powered Misinformation Detection</p>
            </header>

            <main className="app-main">
                <URLInput onSubmit={handleSubmit} isLoading={isAnalyzing && !isComplete} />

                {isAnalyzing && (
                    <>
                        <AgentChain thoughts={thoughts} isComplete={isComplete} />

                        {isComplete && finalResult && (
                            <>
                                <ScoreDisplay
                                    score={finalResult.authenticity_score}
                                    verdict={finalResult.final_verdict}
                                    confidence={finalResult.confidence}
                                />
                                <RedFlagsList redFlags={finalResult.analysis?.red_flags || []} />
                                <SourceCitations
                                    corroborating={finalResult.analysis?.corroborating_sources || []}
                                    contradicting={finalResult.analysis?.contradicting_sources || []}
                                />
                                <ExportReport result={finalResult} />
                            </>
                        )}
                    </>
                )}
            </main>
        </div>
    );
}

export default App;
