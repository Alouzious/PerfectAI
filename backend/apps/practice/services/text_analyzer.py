"""
Text Analyzer Service
Analyzes practice session transcripts
"""
import re
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class TextAnalyzer:
    """Analyze practice session transcripts"""
    
    def __init__(self):
        self.filler_words = [
            'um', 'uh', 'like', 'you know', 'basically', 'actually',
            'literally', 'so', 'well', 'right', 'okay', 'yeah',
            'kind of', 'sort of', 'i mean', 'you see'
        ]
    
    def analyze(self, transcript, duration_seconds=0):
        """
        Analyze transcript and return metrics
        
        Args:
            transcript (str): The practice session transcript
            duration_seconds (int): Duration of practice in seconds
            
        Returns:
            dict: Analysis metrics
        """
        try:
            # Basic metrics
            word_count = self._count_words(transcript)
            sentence_count = self._count_sentences(transcript)
            
            # Calculate speaking pace (WPM)
            if duration_seconds > 0:
                wpm = (word_count / duration_seconds) * 60
            else:
                wpm = 0
            
            # Filler word analysis
            filler_analysis = self._analyze_filler_words(transcript)
            
            # Vocabulary analysis
            unique_words = self._count_unique_words(transcript)
            vocabulary_ratio = unique_words / word_count if word_count > 0 else 0
            
            # Calculate scores
            pace_score = self._calculate_pace_score(wpm)
            clarity_score = self._calculate_clarity_score(filler_analysis['total_count'], word_count)
            
            metrics = {
                'word_count': word_count,
                'sentence_count': sentence_count,
                'unique_words_count': unique_words,
                'vocabulary_ratio': round(vocabulary_ratio, 2),
                'speaking_pace_wpm': round(wpm, 2),
                'filler_words_count': filler_analysis['total_count'],
                'filler_words_detail': filler_analysis['detail'],
                'pace_score': pace_score,
                'clarity_score': clarity_score,
            }
            
            logger.info(f"Analyzed transcript: {word_count} words, {wpm:.1f} WPM")
            return metrics
            
        except Exception as e:
            logger.error(f"Error analyzing transcript: {str(e)}")
            return self._get_default_metrics()
    
    def _count_words(self, text):
        """Count words in text"""
        words = re.findall(r'\b\w+\b', text.lower())
        return len(words)
    
    def _count_sentences(self, text):
        """Count sentences in text"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return len(sentences)
    
    def _count_unique_words(self, text):
        """Count unique words"""
        words = re.findall(r'\b\w+\b', text.lower())
        return len(set(words))
    
    def _analyze_filler_words(self, text):
        """Analyze filler word usage"""
        text_lower = text.lower()
        
        filler_detail = {}
        total_count = 0
        
        for filler in self.filler_words:
            # Use word boundaries to avoid matching within words
            pattern = r'\b' + re.escape(filler) + r'\b'
            count = len(re.findall(pattern, text_lower))
            
            if count > 0:
                filler_detail[filler] = count
                total_count += count
        
        return {
            'total_count': total_count,
            'detail': filler_detail
        }
    
    def _calculate_pace_score(self, wpm):
        """
        Calculate speaking pace score
        Ideal pace: 140-160 WPM
        """
        if wpm == 0:
            return 0
        
        # Ideal range
        if 140 <= wpm <= 160:
            return 100
        
        # Good range
        elif 130 <= wpm < 140 or 160 < wpm <= 170:
            return 90
        
        # Acceptable range
        elif 120 <= wpm < 130 or 170 < wpm <= 180:
            return 75
        
        # Too slow
        elif wpm < 120:
            # Score decreases as pace gets slower
            return max(40, 75 - (120 - wpm) * 2)
        
        # Too fast
        else:  # wpm > 180
            # Score decreases as pace gets faster
            return max(40, 75 - (wpm - 180) * 2)
    
    def _calculate_clarity_score(self, filler_count, word_count):
        """
        Calculate clarity score based on filler word usage
        """
        if word_count == 0:
            return 0
        
        # Calculate filler percentage
        filler_percentage = (filler_count / word_count) * 100
        
        # Excellent: < 1% filler words
        if filler_percentage < 1:
            return 100
        
        # Good: 1-2%
        elif filler_percentage < 2:
            return 90
        
        # Acceptable: 2-3%
        elif filler_percentage < 3:
            return 80
        
        # Needs work: 3-5%
        elif filler_percentage < 5:
            return 70
        
        # Poor: 5%+
        else:
            # Decrease score for higher percentages
            return max(40, 70 - (filler_percentage - 5) * 5)
    
    def _get_default_metrics(self):
        """Return default metrics on error"""
        return {
            'word_count': 0,
            'sentence_count': 0,
            'unique_words_count': 0,
            'vocabulary_ratio': 0,
            'speaking_pace_wpm': 0,
            'filler_words_count': 0,
            'filler_words_detail': {},
            'pace_score': 0,
            'clarity_score': 0,
        }