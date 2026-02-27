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
  MessageSquare,
  ChevronDown,
} from 'lucide-react';

const PITCH_TYPES = [
  { value: 'elevator',    label: 'Elevator Pitch',   duration: 30,  desc: '30 seconds' },
  { value: 'demo_day',    label: 'Demo Day',          duration: 180, desc: '3 minutes' },
  { value: 'competition', label: 'Competition Pitch', duration: 300, desc: '5 minutes' },
  { value: 'investor',    label: 'Investor Pitch',    duration: 600, desc: '10 minutes' },
];

const PracticeRecorder = ({ deckId, onComplete }) => {
  const [isRecording, setIsRecording]   = useState(false);
  const [isPaused, setIsPaused]         = useState(false);
  const [transcript, setTranscript]     = useState('');
  const [interimText, setInterimText]   = useState('');   // live "grey" text while speaking
  const [duration, setDuration]         = useState(0);
  const [analyzing, setAnalyzing]       = useState(false);
  const [feedback, setFeedback]         = useState(null);
  const [error, setError]               = useState('');
  const [pitchType, setPitchType]       = useState('investor');
  const [browserSupported, setBrowserSupported] = useState(true);

  // ── Refs ────────────────────────────────────────────────────────────────────
  const recognitionRef  = useRef(null);
  const timerRef        = useRef(null);
  // These refs mirror state so the onend handler (created once) can read
  // the *current* values without stale-closure issues.
  const isRecordingRef  = useRef(false);
  const isPausedRef     = useRef(false);
  const transcriptRef   = useRef('');   // always in sync with transcript state

  // ── Keep refs in sync with state ────────────────────────────────────────────
  useEffect(() => { isRecordingRef.current  = isRecording;  }, [isRecording]);
  useEffect(() => { isPausedRef.current     = isPaused;     }, [isPaused]);
  useEffect(() => { transcriptRef.current   = transcript;   }, [transcript]);

  // ── Initialise Speech Recognition (once) ────────────────────────────────────
  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setBrowserSupported(false);
      setError(
        '⚠️ Speech recognition is not supported in this browser. ' +
        'Please use Google Chrome or Microsoft Edge.'
      );
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous      = true;
    recognition.interimResults  = true;
    recognition.lang            = 'en-US';
    recognition.maxAlternatives = 1;

    // ── onresult ──────────────────────────────────────────────────────────────
    recognition.onresult = (event) => {
      let finalChunk   = '';
      let interimChunk = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const piece = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalChunk += piece + ' ';
        } else {
          interimChunk += piece;
        }
      }

      if (finalChunk) {
        setTranscript((prev) => prev + finalChunk);
      }
      setInterimText(interimChunk);
    };

    // ── onerror ───────────────────────────────────────────────────────────────
    recognition.onerror = (event) => {
      console.error('SpeechRecognition error:', event.error);

      switch (event.error) {
        case 'no-speech':
          // Harmless — the browser restarts automatically via onend.
          break;
        case 'not-allowed':
        case 'service-not-allowed':
          setError(
            '❌ Microphone access denied. ' +
            'Click the 🔒 icon in your browser address bar, allow the microphone, then reload.'
          );
          setIsRecording(false);
          isRecordingRef.current = false;
          clearInterval(timerRef.current);
          break;
        case 'network':
          setError('❌ Network error with speech recognition. Check your internet connection.');
          setIsRecording(false);
          isRecordingRef.current = false;
          clearInterval(timerRef.current);
          break;
        case 'aborted':
          // We called .stop() intentionally — ignore.
          break;
        default:
          setError(`Speech recognition error: "${event.error}". Please try again.`);
          setIsRecording(false);
          isRecordingRef.current = false;
          clearInterval(timerRef.current);
      }
    };

    // ── onend (KEY FIX — auto-restart while recording is active) ─────────────
    recognition.onend = () => {
      setInterimText('');
      // If the user is still recording and hasn't paused, restart immediately.
      if (isRecordingRef.current && !isPausedRef.current) {
        try {
          recognition.start();
        } catch (err) {
          // InvalidStateError means it's already starting — safe to ignore.
          if (err.name !== 'InvalidStateError') {
            console.error('Failed to restart recognition:', err);
          }
        }
      }
    };

    recognitionRef.current = recognition;

    // Cleanup on unmount
    return () => {
      recognition.onend   = null; // prevent the auto-restart after unmount
      recognition.onerror = null;
      try { recognition.stop(); } catch (_) { /* ignore */ }
      clearInterval(timerRef.current);
    };
  }, []); // runs once

  // ── Helpers ──────────────────────────────────────────────────────────────────
  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  const selectedPitchType = PITCH_TYPES.find((p) => p.value === pitchType);

  // ── Recording controls ───────────────────────────────────────────────────────
  const startRecording = () => {
    if (!recognitionRef.current) {
      setError('Speech recognition is not available.');
      return;
    }

    setError('');
    setTranscript('');
    setInterimText('');
    setDuration(0);
    setFeedback(null);

    setIsRecording(true);
    isRecordingRef.current = true;
    setIsPaused(false);
    isPausedRef.current = false;

    try {
      recognitionRef.current.start();
    } catch (err) {
      if (err.name !== 'InvalidStateError') {
        setError('Could not start microphone: ' + err.message);
        setIsRecording(false);
        isRecordingRef.current = false;
        return;
      }
    }

    timerRef.current = setInterval(() => {
      setDuration((prev) => prev + 1);
    }, 1000);
  };

  const pauseRecording = () => {
    if (!isRecordingRef.current) return;

    // Setting isPausedRef BEFORE calling .stop() so onend won't restart.
    isPausedRef.current = true;
    setIsPaused(true);

    try { recognitionRef.current.stop(); } catch (_) { /* ignore */ }
    clearInterval(timerRef.current);
  };

  const resumeRecording = () => {
    if (!isPausedRef.current) return;

    isPausedRef.current = false;
    setIsPaused(false);

    try {
      recognitionRef.current.start();
    } catch (err) {
      if (err.name !== 'InvalidStateError') {
        setError('Could not resume microphone: ' + err.message);
        return;
      }
    }

    timerRef.current = setInterval(() => {
      setDuration((prev) => prev + 1);
    }, 1000);
  };

  const stopRecording = async () => {
    // Mark as stopped BEFORE calling .stop() so onend won't restart.
    isRecordingRef.current = false;
    isPausedRef.current    = false;
    setIsRecording(false);
    setIsPaused(false);
    setInterimText('');

    try { recognitionRef.current?.stop(); } catch (_) { /* ignore */ }
    clearInterval(timerRef.current);

    // Use the ref for the latest transcript value (state may be one render behind).
    const finalTranscript = transcriptRef.current.trim();

    if (finalTranscript.length >= 10) {
      await submitForAnalysis(finalTranscript);
    } else {
      setError(
        finalTranscript.length === 0
          ? '🎤 No speech was captured. Make sure your microphone is working and try again.'
          : '🎤 Too little speech captured. Please practice for at least a few seconds.'
      );
    }
  };

  // ── Submit to backend ─────────────────────────────────────────────────────────
  const submitForAnalysis = async (finalTranscript) => {
    setAnalyzing(true);
    setError('');

    try {
      const response = await practiceAPI.create({
        pitch_deck:               deckId,
        pitch_type:               pitchType,
        transcript:               finalTranscript,
        duration_seconds:         duration,
        target_duration_seconds:  selectedPitchType?.duration ?? 600,
      });

      // Poll until the Celery task marks the session as completed.
      const result = await poll(
        () => practiceAPI.getFeedback(response.session.id),
        (data) => data.session_id && data.overall_score !== undefined,
        2000,  // poll every 2 s
        60     // max 60 attempts (2 minutes)
      );

      setFeedback(result);
      setAnalyzing(false);
      onComplete?.(result);
    } catch (err) {
      setAnalyzing(false);
      setError(err.message || 'Analysis failed. Please try again.');
    }
  };

  // ── Reset to record again ────────────────────────────────────────────────────
  const resetRecorder = () => {
    setFeedback(null);
    setTranscript('');
    setInterimText('');
    setDuration(0);
    setError('');
  };

  // ════════════════════════════════════════════════════════════════════════════
  // RENDER
  // ════════════════════════════════════════════════════════════════════════════
  return (
    <div className="space-y-6">

      {/* ── Error banner ── */}
      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/50 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
          <p className="text-red-200 text-sm">{error}</p>
        </div>
      )}

      {/* ── Not-supported fallback ── */}
      {!browserSupported && (
        <div className="p-6 bg-yellow-500/10 border border-yellow-500/30 rounded-xl text-center">
          <p className="text-yellow-300 font-semibold mb-2">Browser Not Supported</p>
          <p className="text-yellow-200 text-sm">
            Please open this page in <strong>Google Chrome</strong> or{' '}
            <strong>Microsoft Edge</strong> to use the microphone feature.
          </p>
        </div>
      )}

      {/* ══════════════════════════════════════════════
          STATE 1 — Recording Interface
      ══════════════════════════════════════════════ */}
      {browserSupported && !analyzing && !feedback && (
        <>
          {/* Pitch-type selector (only shown before recording starts) */}
          {!isRecording && (
            <div className="bg-white/5 border border-white/10 rounded-xl p-4">
              <label className="block text-gray-400 text-sm mb-2">Pitch Type</label>
              <div className="relative">
                <select
                  value={pitchType}
                  onChange={(e) => setPitchType(e.target.value)}
                  className="w-full bg-white/10 border border-white/20 text-white rounded-lg px-4 py-3 appearance-none cursor-pointer focus:outline-none focus:border-purple-500"
                >
                  {PITCH_TYPES.map((pt) => (
                    <option key={pt.value} value={pt.value} className="bg-slate-800">
                      {pt.label} — {pt.desc}
                    </option>
                  ))}
                </select>
                <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
              </div>
            </div>
          )}

          {/* Mic + timer */}
          <div className="bg-white/5 border border-white/10 rounded-xl p-8 text-center">
            {/* Visualisation ring */}
            <div
              className={`w-24 h-24 mx-auto mb-6 rounded-full flex items-center justify-center transition-all duration-300 ${
                isRecording && !isPaused
                  ? 'bg-red-500/20 animate-pulse ring-4 ring-red-500/30'
                  : isPaused
                  ? 'bg-yellow-500/20 ring-4 ring-yellow-500/30'
                  : 'bg-purple-500/20'
              }`}
            >
              <Mic
                className={`w-12 h-12 ${
                  isRecording && !isPaused
                    ? 'text-red-400'
                    : isPaused
                    ? 'text-yellow-400'
                    : 'text-purple-400'
                }`}
              />
            </div>

            {/* Timer */}
            <div className="text-4xl font-bold text-white mb-1 font-mono tabular-nums">
              {formatTime(duration)}
            </div>

            {/* Target duration hint */}
            {isRecording && selectedPitchType && (
              <p className="text-gray-500 text-xs mb-2">
                Target: {selectedPitchType.desc} ({formatTime(selectedPitchType.duration)})
              </p>
            )}

            {/* Status text */}
            <p className="text-gray-400 mb-8">
              {isRecording
                ? isPaused
                  ? '⏸ Recording paused — click Resume to continue'
                  : '🔴 Recording in progress… speak clearly'
                : 'Click Start Recording to begin your practice session'}
            </p>

            {/* Controls */}
            <div className="flex items-center justify-center gap-4 flex-wrap">
              {!isRecording ? (
                <button
                  onClick={startRecording}
                  className="px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-semibold hover:opacity-90 transition-all flex items-center gap-2 shadow-lg"
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
                    Stop &amp; Analyze
                  </button>
                </>
              )}
            </div>
          </div>

          {/* Live transcript box */}
          {(transcript || interimText) && (
            <div className="bg-white/5 border border-white/10 rounded-xl p-6">
              <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
                <MessageSquare className="w-5 h-5 text-purple-400" />
                Live Transcript
                <span className="ml-auto text-gray-500 text-xs font-normal">
                  {transcript.trim().split(/\s+/).filter(Boolean).length} words
                </span>
              </h3>
              <div className="max-h-48 overflow-y-auto text-sm leading-relaxed">
                <span className="text-gray-300">{transcript}</span>
                {interimText && (
                  <span className="text-gray-500 italic">{interimText}</span>
                )}
                {!transcript && !interimText && (
                  <span className="text-gray-600">Your speech will appear here…</span>
                )}
              </div>
            </div>
          )}
        </>
      )}

      {/* ══════════════════════════════════════════════
          STATE 2 — Analyzing
      ══════════════════════════════════════════════ */}
      {analyzing && (
        <div className="text-center py-16">
          <div className="w-20 h-20 bg-purple-500/20 rounded-2xl flex items-center justify-center mx-auto mb-6 animate-pulse">
            <Loader2 className="w-10 h-10 text-purple-400 animate-spin" />
          </div>
          <h3 className="text-2xl font-bold text-white mb-3">Analyzing Your Pitch</h3>
          <p className="text-gray-400">
            Our AI is evaluating your delivery, pace, clarity, and content…
          </p>
          <p className="text-gray-600 text-sm mt-2">This may take up to 30 seconds</p>
        </div>
      )}

      {/* ══════════════════════════════════════════════
          STATE 3 — Feedback Results
      ══════════════════════════════════════════════ */}
      {feedback && !analyzing && (
        <div className="space-y-6">

          {/* Overall score hero */}
          <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl p-8 text-center shadow-xl">
            <div className="text-7xl font-bold text-white mb-2">
              {Math.round(feedback.overall_score)}
            </div>
            <p className="text-purple-100 text-lg font-medium">Overall Score</p>
            <p className="text-purple-200 text-sm mt-1 capitalize">
              {selectedPitchType?.label} · {formatTime(feedback.metrics?.duration_seconds ?? duration)}
            </p>
          </div>

          {/* Score breakdown */}
          {feedback.scores && (
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
              {Object.entries(feedback.scores).map(([key, value]) => (
                <div
                  key={key}
                  className="bg-white/5 border border-white/10 rounded-lg p-4 text-center"
                >
                  <div className="text-2xl font-bold text-white mb-1">
                    {Math.round(value)}
                  </div>
                  <p className="text-gray-400 text-xs capitalize">
                    {key.replace(/_/g, ' ')}
                  </p>
                </div>
              ))}
            </div>
          )}

          {/* Metrics row */}
          {feedback.metrics && (
            <div className="bg-white/5 border border-white/10 rounded-xl p-6">
              <h3 className="text-white font-semibold mb-4">Performance Metrics</h3>
              <div className="grid sm:grid-cols-3 gap-4">
                <div className="flex items-center gap-3">
                  <Clock className="w-8 h-8 text-blue-400 flex-shrink-0" />
                  <div>
                    <p className="text-white font-medium">
                      {Math.round(feedback.metrics.speaking_pace_wpm ?? 0)} WPM
                    </p>
                    <p className="text-gray-400 text-xs">Speaking Pace</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <MessageSquare className="w-8 h-8 text-green-400 flex-shrink-0" />
                  <div>
                    <p className="text-white font-medium">
                      {feedback.metrics.word_count ?? 0} words
                    </p>
                    <p className="text-gray-400 text-xs">Total Words</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <AlertCircle className="w-8 h-8 text-yellow-400 flex-shrink-0" />
                  <div>
                    <p className="text-white font-medium">
                      {feedback.metrics.filler_words_count ?? 0} filler words
                    </p>
                    <p className="text-gray-400 text-xs">um, uh, like…</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* AI narrative feedback */}
          <div className="bg-white/5 border border-white/10 rounded-xl p-6">
            <h3 className="text-white font-semibold mb-3">AI Coach Feedback</h3>
            <p className="text-gray-300 text-sm leading-relaxed mb-5">
              {feedback.feedback}
            </p>

            {/* Strengths */}
            {feedback.strengths?.length > 0 && (
              <div className="mb-4">
                <h4 className="text-green-400 font-semibold text-sm mb-2 flex items-center gap-1">
                  <CheckCircle2 className="w-4 h-4" /> Strengths
                </h4>
                <ul className="space-y-1">
                  {feedback.strengths.map((s, i) => (
                    <li key={i} className="text-green-200 text-sm flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 mt-0.5 flex-shrink-0" />
                      {s}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Improvements */}
            {feedback.improvements?.length > 0 && (
              <div>
                <h4 className="text-orange-400 font-semibold text-sm mb-2 flex items-center gap-1">
                  <TrendingUp className="w-4 h-4" /> Areas to Improve
                </h4>
                <ul className="space-y-1">
                  {feedback.improvements.map((imp, i) => (
                    <li key={i} className="text-orange-200 text-sm flex items-start gap-2">
                      <TrendingUp className="w-4 h-4 mt-0.5 flex-shrink-0" />
                      {imp}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Action buttons */}
          <div className="flex gap-4">
            <button
              onClick={resetRecorder}
              className="flex-1 px-6 py-3 bg-white/10 hover:bg-white/20 border border-white/20 text-white rounded-lg font-semibold transition-all"
            >
              Practice Again
            </button>
            <button
              onClick={() => onComplete?.(feedback)}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-semibold hover:opacity-90 transition-all shadow-lg"
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