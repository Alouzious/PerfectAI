import { useState, useEffect } from 'react';
import { pitchAPI } from '../../services/api';
import Modal from '../common/Modal';
import Tabs from '../common/Tabs';
import PracticeRecorder from '../practice/PracticeRecorder';
import QASection from '../qa/QASection';
import { FileText, Mic, MessageSquare, Loader2, ChevronLeft, ChevronRight, CheckCircle2 } from 'lucide-react';

const PitchDeckModal = ({ isOpen, onClose, deckId }) => {
  const [loading, setLoading] = useState(true);
  const [deck, setDeck] = useState(null);
  const [slides, setSlides] = useState([]);
  const [activeTab, setActiveTab] = useState('slides');
  const [currentSlide, setCurrentSlide] = useState(0);

  useEffect(() => {
    if (isOpen && deckId) {
      fetchDeckData();
    }
  }, [isOpen, deckId]);

  const fetchDeckData = async () => {
    try {
      setLoading(true);
      const [deckData, slidesData] = await Promise.all([
        pitchAPI.get(deckId),
        pitchAPI.getSlides(deckId)
      ]);
      setDeck(deckData);
      setSlides(slidesData.slides || []);
    } catch (error) {
      console.error('Error fetching deck:', error);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'slides', label: 'Slides', icon: <FileText className="w-4 h-4" /> },
    { id: 'practice', label: 'Practice', icon: <Mic className="w-4 h-4" /> },
    { id: 'qa', label: 'Q&A', icon: <MessageSquare className="w-4 h-4" /> }
  ];

  const currentSlideData = slides[currentSlide];

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={deck?.title || 'Pitch Deck'} size="xl">
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-10 h-10 text-purple-500 animate-spin" />
        </div>
      ) : (
        <>
          <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />

          {activeTab === 'slides' && (
            <div className="space-y-6">
              {/* Slide Navigation */}
              <div className="flex items-center justify-between bg-white/5 rounded-lg p-4">
                <button
                  onClick={() => setCurrentSlide(Math.max(0, currentSlide - 1))}
                  disabled={currentSlide === 0}
                  className="p-2 text-gray-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                
                <span className="text-white font-medium">
                  Slide {currentSlide + 1} of {slides.length}
                </span>
                
                <button
                  onClick={() => setCurrentSlide(Math.min(slides.length - 1, currentSlide + 1))}
                  disabled={currentSlide === slides.length - 1}
                  className="p-2 text-gray-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>

              {/* Slide Content */}
              {currentSlideData && (
                <div className="space-y-4">
                  {/* Slide Preview */}
                  <div className="bg-white/5 border border-white/10 rounded-lg p-6">
                    <h3 className="text-white font-semibold mb-3 capitalize">
                      {currentSlideData.slide_type?.replace('_', ' ')}
                    </h3>
                    <p className="text-gray-300 text-sm leading-relaxed">
                      {currentSlideData.text_content || 'No text content'}
                    </p>
                  </div>

                  {/* Analysis */}
                  <div className="grid sm:grid-cols-2 gap-4">
                    {/* Strengths */}
                    <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4">
                      <h4 className="text-green-400 font-semibold mb-2 text-sm">Strengths</h4>
                      <ul className="space-y-1">
                        {currentSlideData.strengths?.map((strength, i) => (
                          <li key={i} className="text-green-200 text-sm flex items-start gap-2">
                            <CheckCircle2 className="w-4 h-4 mt-0.5 flex-shrink-0" />
                            {strength}
                          </li>
                        )) || <li className="text-green-200 text-sm">No strengths analyzed yet</li>}
                      </ul>
                    </div>

                    {/* Weaknesses */}
                    <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                      <h4 className="text-red-400 font-semibold mb-2 text-sm">Areas to Improve</h4>
                      <ul className="space-y-1">
                        {currentSlideData.weaknesses?.map((weakness, i) => (
                          <li key={i} className="text-red-200 text-sm">• {weakness}</li>
                        )) || <li className="text-red-200 text-sm">No weaknesses identified</li>}
                      </ul>
                    </div>
                  </div>

                  {/* Coaching Script */}
                  {currentSlideData.suggested_script && (
                    <div className="bg-purple-500/10 border border-purple-500/30 rounded-lg p-4">
                      <h4 className="text-purple-400 font-semibold mb-2 text-sm">Coaching Script</h4>
                      <p className="text-purple-200 text-sm leading-relaxed">
                        {currentSlideData.suggested_script}
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {activeTab === 'practice' && (
            <PracticeRecorder 
              deckId={deckId}
              onComplete={() => {
                // Optionally refresh deck stats or show success message
              }}
            />
          )}

          {activeTab === 'qa' && (
            <QASection deckId={deckId} />
          )}
        </>
      )}
    </Modal>
  );
};

export default PitchDeckModal;