import { useState, useRef, useEffect } from 'react';
import { practiceAPI, poll } from '../../services/api';
import { 
  Mic, 
  Square, 
  Play, 
  Pause,
  Loader2, 
  CheckCircle2,
  AlertCircle,
  TrendingUp,
  Clock,
  MessageSquare
} from 'lucide-react';

const PracticeRecorder = ({ deckId, onComplete }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [duration, setDuration] = useState(0);
  const [analyzing, setAnalyzing] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [error, setError] = useState('');

  const recognitionRef = useRef(null);
  const timerRef = useRef(null);

  useEffect(() => {
    // Initialize Speech Recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcriptPiece = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcriptPiece + ' ';
          } else {
            interimTranscript += transcriptPiece;
          }
        }

        setTranscript(prev => prev + finalTranscript);
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        if (event.error === 'no-speech') {
          setError('No speech detected. Please try again.');
        }
      };
    } else {
      setError('Speech recognition is not supported in your browser. Please use Chrome or Edge.');
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, []);

  const startRecording = () => {
    if (!recognitionRef.current) {
      setError('Speech recognition not available');
      return;
    }

    setError('');
    setTranscript('');
    setDuration(0);
    setIsRecording(true);
    setIsPaused(false);

    recognitionRef.current.start();

    // Start timer
    timerRef.current = setInterval(() => {
      setDuration(prev => prev + 1);
    }, 1000);
  };

  const pauseRecording = () => {
    if (recognitionRef.current && isRecording) {
      recognitionRef.current.stop();
      clearInterval(timerRef.current);
      setIsPaused(true);
    }
  };

  const resumeRecording = () => {
    if (recognitionRef.current && isPaused) {
      recognitionRef.current.start();
      timerRef.current = setInterval(() => {
        setDuration(prev => prev + 1);
      }, 1000);
      setIsPaused(false);
    }
  };

  const stopRecording = async () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    clearInterval(timerRef.current);
    setIsRecording(false);
    setIsPaused(false);

    // Submit for analysis
    if (transcript.trim()) {
      await submitForAnalysis();
    } else {
      setError('No speech was recorded. Please try again.');
    }
  };

  const submitForAnalysis = async () => {
    setAnalyzing(true);
    setError('');

    try {
      // Create practice session
      const response = await practiceAPI.create({
        pitch_deck: deckId,
        pitch_type: 'investor',
        transcript: transcript,
        duration_seconds: duration,
        target_duration_seconds: 600 // 10 minutes default
      });

      // Poll for feedback
      const result = await poll(
        () => practiceAPI.getFeedback(response.session.id),
        (data) => data.session_id && data.overall_score !== undefined,
        2000,
        60
      );

      setFeedback(result);
      setAnalyzing(false);

      if (onComplete) {
        onComplete(result);
      }

    } catch (err) {
      setAnalyzing(false);
      setError(err.message || 'Analysis failed. Please try again.');
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-6">
      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/50 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
          <p className="text-red-200 text-sm">{error}</p>
        </div>
      )}

      {!analyzing && !feedback ? (
        <>
          {/* Recording Interface */}
          <div className="bg-white/5 border border-white/10 rounded-xl p-8 text-center">
            {/* Microphone Visualization */}
            <div className={`w-24 h-24 mx-auto mb-6 rounded-full flex items-center justify-center transition-all ${
              isRecording && !isPaused
                ? 'bg-red-500/20 animate-pulse'
                : 'bg-purple-500/20'
            }`}>
              <Mic className={`w-12 h-12 ${
                isRecording && !isPaused ? 'text-red-400' : 'text-purple-400'
              }`} />
            </div>

            {/* Timer */}
            <div className="text-4xl font-bold text-white mb-2">
              {formatTime(duration)}
            </div>

            {/* Status */}
            <p className="text-gray-400 mb-8">
              {isRecording 
                ? isPaused ? 'Recording paused' : 'Recording in progress...'
                : 'Click start to begin recording'}
            </p>

            {/* Controls */}
            <div className="flex items-center justify-center gap-4">
              {!isRecording ? (
                <button
                  onClick={startRecording}
                  className="px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-semibold hover:shadow-glow transition-all flex items-center gap-2"
                >
                  <Mic className="w-5 h-5" />
                  Start Recording
                </button>
              ) : (
                <>
                  {!isPaused ? (
                    <button
                      onClick={pauseRecording}
                      className="px-6 py-3 bg-yellow-500/20 border border-yellow-500/30 text-yellow-400 rounded-lg font-semibold hover:bg-yellow-500/30 transition-all flex items-center gap-2"
                    >
                      <Pause className="w-5 h-5" />
                      Pause
                    </button>
                  ) : (
                    <button
                      onClick={resumeRecording}
                      className="px-6 py-3 bg-green-500/20 border border-green-500/30 text-green-400 rounded-lg font-semibold hover:bg-green-500/30 transition-all flex items-center gap-2"
                    >
                      <Play className="w-5 h-5" />
                      Resume
                    </button>
                  )}
                  
                  <button
                    onClick={stopRecording}
                    className="px-6 py-3 bg-red-500/20 border border-red-500/30 text-red-400 rounded-lg font-semibold hover:bg-red-500/30 transition-all flex items-center gap-2"
                  >
                    <Square className="w-5 h-5" />
                    Stop & Analyze
                  </button>
                </>
              )}
            </div>
          </div>

          {/* Live Transcript */}
          {transcript && (
            <div className="bg-white/5 border border-white/10 rounded-xl p-6">
              <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
                <MessageSquare className="w-5 h-5" />
                Live Transcript
              </h3>
              <div className="max-h-48 overflow-y-auto text-gray-300 text-sm leading-relaxed">
                {transcript || 'Your speech will appear here...'}
              </div>
            </div>
          )}
        </>
      ) : analyzing ? (
        /* Analyzing State */
        <div className="text-center py-12">
          <div className="w-20 h-20 bg-purple-500/20 rounded-2xl flex items-center justify-center mx-auto mb-6 animate-pulse">
            <Loader2 className="w-10 h-10 text-purple-400 animate-spin" />
          </div>
          <h3 className="text-2xl font-bold text-white mb-3">
            Analyzing Your Pitch
          </h3>
          <p className="text-gray-400">
            Our AI is evaluating your delivery, pace, clarity, and content...
          </p>
        </div>
      ) : (
        /* Feedback Results */
        <div className="space-y-6">
          {/* Overall Score */}
          <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl p-6 text-center">
            <div className="text-6xl font-bold text-white mb-2">
              {Math.round(feedback.overall_score)}
            </div>
            <p className="text-purple-100 text-lg">Overall Score</p>
          </div>

          {/* Score Breakdown */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
            {Object.entries(feedback.scores || {}).map(([key, value]) => (
              <div key={key} className="bg-white/5 border border-white/10 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-white mb-1">
                  {Math.round(value)}
                </div>
                <p className="text-gray-400 text-xs capitalize">
                  {key.replace('_', ' ')}
                </p>
              </div>
            ))}
          </div>

          {/* Metrics */}
          <div className="bg-white/5 border border-white/10 rounded-xl p-6">
            <h3 className="text-white font-semibold mb-4">Performance Metrics</h3>
            <div className="grid sm:grid-cols-3 gap-4">
              <div className="flex items-center gap-3">
                <Clock className="w-8 h-8 text-blue-400" />
                <div>
                  <p className="text-white font-medium">
                    {feedback.metrics?.speaking_pace_wpm} WPM
                  </p>
                  <p className="text-gray-400 text-xs">Speaking Pace</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <MessageSquare className="w-8 h-8 text-green-400" />
                <div>
                  <p className="text-white font-medium">
                    {feedback.metrics?.word_count} words
                  </p>
                  <p className="text-gray-400 text-xs">Total Words</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <AlertCircle className="w-8 h-8 text-yellow-400" />
                <div>
                  <p className="text-white font-medium">
                    {feedback.metrics?.filler_words_count} filler words
                  </p>
                  <p className="text-gray-400 text-xs">Um, uh, like...</p>
                </div>
              </div>
            </div>
          </div>

          {/* Feedback */}
          <div className="bg-white/5 border border-white/10 rounded-xl p-6">
            <h3 className="text-white font-semibold mb-3">AI Feedback</h3>
            <p className="text-gray-300 text-sm leading-relaxed mb-4">
              {feedback.feedback}
            </p>

            {/* Strengths */}
            <div className="mb-4">
              <h4 className="text-green-400 font-semibold text-sm mb-2">Strengths</h4>
              <ul className="space-y-1">
                {feedback.strengths?.map((strength, i) => (
                  <li key={i} className="text-green-200 text-sm flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 mt-0.5 flex-shrink-0" />
                    {strength}
                  </li>
                ))}
              </ul>
            </div>

            {/* Improvements */}
            <div>
              <h4 className="text-orange-400 font-semibold text-sm mb-2">Areas to Improve</h4>
              <ul className="space-y-1">
                {feedback.improvements?.map((improvement, i) => (
                  <li key={i} className="text-orange-200 text-sm flex items-start gap-2">
                    <TrendingUp className="w-4 h-4 mt-0.5 flex-shrink-0" />
                    {improvement}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-4">
            <button
              onClick={() => {
                setFeedback(null);
                setTranscript('');
                setDuration(0);
              }}
              className="flex-1 px-6 py-3 bg-white/10 hover:bg-white/20 border border-white/20 text-white rounded-lg font-semibold transition-all"
            >
              Practice Again
            </button>
            <button
              onClick={() => onComplete && onComplete(feedback)}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-semibold hover:shadow-glow transition-all"
            >
              Done
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default PracticeRecorder;