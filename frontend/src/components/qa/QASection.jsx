import { useState, useEffect } from 'react';
import { qaAPI, poll } from '../../services/api';
import { 
  MessageSquare, 
  Loader2, 
  CheckCircle2,
  AlertCircle,
  Send,
  Sparkles,
  TrendingUp
} from 'lucide-react';

const QASection = ({ deckId }) => {
  const [loading, setLoading] = useState(true);
  const [questions, setQuestions] = useState([]);
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [answer, setAnswer] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchQuestions();
  }, [deckId]);

  const fetchQuestions = async () => {
    try {
      setLoading(true);
      const data = await qaAPI.getQuestions(deckId);
      
      if (data.questions && data.questions.length > 0) {
        setQuestions(data.questions);
      } else {
        // Questions are being generated
        setTimeout(() => fetchQuestions(), 5000); // Retry after 5 seconds
      }
    } catch (err) {
      console.error('Error fetching questions:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!answer.trim() || !selectedQuestion) {
      setError('Please provide an answer');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      const response = await qaAPI.submitAnswer({
        question: selectedQuestion.id,
        answer_text: answer,
        answer_duration_seconds: 0
      });

      // Poll for feedback
      const result = await poll(
        () => qaAPI.getAnswer(response.answer.id),
        (data) => data.status === 'completed',
        2000,
        30
      );

      setFeedback(result);
      setSubmitting(false);

    } catch (err) {
      setSubmitting(false);
      setError(err.message || 'Failed to submit answer');
    }
  };

  const resetAnswer = () => {
    setAnswer('');
    setFeedback(null);
    setSelectedQuestion(null);
  };

  const getDifficultyColor = (difficulty) => {
    const colors = {
      easy: 'text-green-400 bg-green-500/20 border-green-500/30',
      medium: 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30',
      hard: 'text-red-400 bg-red-500/20 border-red-500/30'
    };
    return colors[difficulty] || colors.medium;
  };

  const getCategoryColor = (category) => {
    const colors = {
      market: 'text-blue-400',
      competition: 'text-purple-400',
      business_model: 'text-green-400',
      team: 'text-orange-400',
      traction: 'text-pink-400',
      financials: 'text-yellow-400',
      product: 'text-cyan-400',
      risks: 'text-red-400'
    };
    return colors[category] || 'text-gray-400';
  };

  return (
    <div className="space-y-6">
      {loading ? (
        <div className="text-center py-12">
          <Loader2 className="w-10 h-10 text-purple-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Generating investor questions...</p>
        </div>
      ) : questions.length === 0 ? (
        <div className="text-center py-12">
          <Sparkles className="w-16 h-16 text-purple-400 mx-auto mb-4" />
          <h3 className="text-white font-semibold text-lg mb-2">No Questions Yet</h3>
          <p className="text-gray-400">Questions are being generated. Please wait...</p>
        </div>
      ) : !selectedQuestion ? (
        /* Question List */
        <div className="space-y-4">
          <h3 className="text-white font-semibold text-lg mb-4">
            Practice Investor Questions ({questions.length})
          </h3>
          
          {questions.map((question, index) => (
            <button
              key={question.id}
              onClick={() => setSelectedQuestion(question)}
              className="w-full text-left bg-white/5 hover:bg-white/10 border border-white/10 hover:border-purple-500/50 rounded-xl p-4 sm:p-6 transition-all group"
            >
              <div className="flex items-start justify-between gap-4 mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-purple-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                    <span className="text-purple-400 font-bold text-sm">
                      {index + 1}
                    </span>
                  </div>
                  <span className={`px-3 py-1 rounded-lg text-xs font-medium border ${getDifficultyColor(question.difficulty)}`}>
                    {question.difficulty}
                  </span>
                </div>
                
                <span className={`text-xs font-medium capitalize ${getCategoryColor(question.category)}`}>
                  {question.category?.replace('_', ' ')}
                </span>
              </div>
              
              <p className="text-white group-hover:text-purple-300 transition-colors text-sm sm:text-base">
                {question.question_text}
              </p>
            </button>
          ))}
        </div>
      ) : !feedback ? (
        /* Answer Interface */
        <div className="space-y-6">
          {/* Question */}
          <div className="bg-purple-500/10 border border-purple-500/30 rounded-xl p-6">
            <div className="flex items-center gap-3 mb-3">
              <span className={`px-3 py-1 rounded-lg text-xs font-medium border ${getDifficultyColor(selectedQuestion.difficulty)}`}>
                {selectedQuestion.difficulty}
              </span>
              <span className={`text-xs font-medium capitalize ${getCategoryColor(selectedQuestion.category)}`}>
                {selectedQuestion.category?.replace('_', ' ')}
              </span>
            </div>
            <p className="text-white font-semibold text-lg">
              {selectedQuestion.question_text}
            </p>
          </div>

          {/* Error */}
          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/50 rounded-lg flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
              <p className="text-red-200 text-sm">{error}</p>
            </div>
          )}

          {/* Answer Input */}
          <div>
            <label className="block text-white font-medium mb-3 text-sm">
              Your Answer
            </label>
            <textarea
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="Type your answer here... Be specific and demonstrate your knowledge."
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all resize-none"
              rows="8"
              disabled={submitting}
            />
            <p className="text-gray-400 text-xs mt-2">
              {answer.split(' ').filter(w => w).length} words
            </p>
          </div>

          {/* Actions */}
          <div className="flex gap-4">
            <button
              onClick={() => setSelectedQuestion(null)}
              className="px-6 py-3 bg-white/10 hover:bg-white/20 border border-white/20 text-white rounded-lg font-semibold transition-all"
              disabled={submitting}
            >
              Back to Questions
            </button>
            <button
              onClick={handleSubmitAnswer}
              disabled={!answer.trim() || submitting}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-semibold hover:shadow-glow transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  Submit Answer
                </>
              )}
            </button>
          </div>
        </div>
      ) : (
        /* Feedback Results */
        <div className="space-y-6">
          {/* Score */}
          <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl p-6 text-center">
            <div className="text-5xl font-bold text-white mb-2">
              {Math.round(feedback.quality_score)}
            </div>
            <p className="text-purple-100">Answer Quality Score</p>
          </div>

          {/* Score Breakdown */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-white/5 border border-white/10 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-white mb-1">
                {Math.round(feedback.completeness_score)}
              </div>
              <p className="text-gray-400 text-xs">Completeness</p>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-white mb-1">
                {Math.round(feedback.clarity_score)}
              </div>
              <p className="text-gray-400 text-xs">Clarity</p>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-white mb-1">
                {Math.round(feedback.confidence_score)}
              </div>
              <p className="text-gray-400 text-xs">Confidence</p>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-white mb-1">
                {Math.round(feedback.relevance_score)}
              </div>
              <p className="text-gray-400 text-xs">Relevance</p>
            </div>
          </div>

          {/* Feedback */}
          <div className="bg-white/5 border border-white/10 rounded-xl p-6">
            <h3 className="text-white font-semibold mb-3">AI Feedback</h3>
            <p className="text-gray-300 text-sm leading-relaxed mb-4">
              {feedback.feedback}
            </p>

            {/* Strong Points */}
            {feedback.strong_points && feedback.strong_points.length > 0 && (
              <div className="mb-4">
                <h4 className="text-green-400 font-semibold text-sm mb-2">Strong Points</h4>
                <ul className="space-y-1">
                  {feedback.strong_points.map((point, i) => (
                    <li key={i} className="text-green-200 text-sm flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 mt-0.5 flex-shrink-0" />
                      {point}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Improvements */}
            {feedback.improvements && feedback.improvements.length > 0 && (
              <div>
                <h4 className="text-orange-400 font-semibold text-sm mb-2">Improvements</h4>
                <ul className="space-y-1">
                  {feedback.improvements.map((improvement, i) => (
                    <li key={i} className="text-orange-200 text-sm flex items-start gap-2">
                      <TrendingUp className="w-4 h-4 mt-0.5 flex-shrink-0" />
                      {improvement}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Suggested Answer */}
          {feedback.suggested_answer && (
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-6">
              <h3 className="text-blue-400 font-semibold mb-3 text-sm">
                Suggested Answer Approach
              </h3>
              <p className="text-blue-200 text-sm leading-relaxed">
                {feedback.suggested_answer}
              </p>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-4">
            <button
              onClick={resetAnswer}
              className="flex-1 px-6 py-3 bg-white/10 hover:bg-white/20 border border-white/20 text-white rounded-lg font-semibold transition-all"
            >
              Try Another Question
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default QASection;