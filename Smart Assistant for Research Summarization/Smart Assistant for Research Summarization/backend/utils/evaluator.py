"""
Answer Evaluator for NeuraDoc
Evaluates user answers using semantic similarity and keyword analysis
"""

import re
import numpy as np
from typing import Dict, List
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords


class AnswerEvaluator:
    """Evaluates user answers using semantic similarity and keyword analysis"""
    
    def __init__(self):
        # Initialize sentence transformer for semantic similarity
        try:
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Warning: Could not load sentence transformer: {e}")
            self.embedder = None
        
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        self.stop_words = set(stopwords.words('english'))
    
    def evaluate_answer(self, question: Dict, user_answer: str, document_text: str) -> Dict:
        """
        Evaluate user's answer to a challenge question
        
        Args:
            question: Question dictionary with question text and concepts
            user_answer: User's submitted answer
            document_text: Full document text for context
            
        Returns:
            Evaluation dictionary with score, feedback, and analysis
        """
        if not user_answer or not question:
            return self._create_evaluation(0, "No answer provided", "Please provide a detailed answer.")
        
        try:
            # Extract relevant information from document
            relevant_sentences = self._find_relevant_sentences(
                question['question'], document_text
            )
            
            if not relevant_sentences:
                return self._create_evaluation(
                    0.5, 
                    "Limited context available", 
                    "I couldn't find specific information to evaluate your answer against."
                )
            
            # Calculate semantic similarity
            semantic_score = self._calculate_semantic_similarity(
                user_answer, relevant_sentences
            )
            
            # Calculate keyword overlap
            keyword_score = self._calculate_keyword_overlap(
                user_answer, question.get('concepts', []), document_text
            )
            
            # Calculate content relevance
            content_score = self._calculate_content_relevance(
                user_answer, relevant_sentences
            )
            
            # Combine scores
            overall_score = self._combine_scores(semantic_score, keyword_score, content_score)
            
            # Generate feedback
            feedback = self._generate_feedback(
                overall_score, semantic_score, keyword_score, content_score, user_answer
            )
            
            # Generate detailed analysis
            analysis = self._generate_analysis(
                question, user_answer, relevant_sentences, overall_score
            )
            
            return self._create_evaluation(overall_score, feedback, analysis)
            
        except Exception as e:
            print(f"Answer evaluation failed: {e}")
            return self._create_evaluation(
                0.5, 
                "Evaluation error", 
                "I encountered an error while evaluating your answer. Please try again."
            )
    
    def _find_relevant_sentences(self, question: str, document_text: str) -> List[str]:
        """Find sentences relevant to the question"""
        sentences = self._split_into_sentences(document_text)
        
        if not self.embedder:
            # Fallback: return first few sentences
            return sentences[:5]
        
        try:
            # Encode question and sentences
            question_embedding = self.embedder.encode([question])
            sentence_embeddings = self.embedder.encode(sentences)
            
            # Calculate similarities
            similarities = cosine_similarity(question_embedding, sentence_embeddings)[0]
            
            # Get top relevant sentences
            top_indices = np.argsort(similarities)[::-1][:5]
            relevant_sentences = [sentences[i] for i in top_indices if similarities[i] > 0.3]
            
            return relevant_sentences if relevant_sentences else sentences[:3]
            
        except Exception as e:
            print(f"Semantic search failed: {e}")
            return sentences[:3]
    
    def _calculate_semantic_similarity(self, user_answer: str, relevant_sentences: List[str]) -> float:
        """Calculate semantic similarity between user answer and relevant sentences"""
        if not self.embedder or not relevant_sentences:
            return 0.5
        
        try:
            # Encode user answer and relevant sentences
            answer_embedding = self.embedder.encode([user_answer])
            sentence_embeddings = self.embedder.encode(relevant_sentences)
            
            # Calculate similarities
            similarities = cosine_similarity(answer_embedding, sentence_embeddings)[0]
            
            # Return average similarity
            return float(np.mean(similarities))
            
        except Exception as e:
            print(f"Semantic similarity calculation failed: {e}")
            return 0.5
    
    def _calculate_keyword_overlap(self, user_answer: str, expected_concepts: List[str], document_text: str) -> float:
        """Calculate keyword overlap between user answer and expected concepts"""
        if not expected_concepts:
            return 0.5
        
        # Extract keywords from user answer
        answer_words = set(re.findall(r'\b\w+\b', user_answer.lower()))
        answer_words = {w for w in answer_words if w not in self.stop_words and len(w) > 3}
        
        # Calculate overlap with expected concepts
        concept_words = set()
        for concept in expected_concepts:
            concept_words.update(re.findall(r'\b\w+\b', concept.lower()))
        
        if not concept_words:
            return 0.5
        
        overlap = len(answer_words.intersection(concept_words))
        overlap_score = overlap / len(concept_words)
        
        return min(overlap_score, 1.0)
    
    def _calculate_content_relevance(self, user_answer: str, relevant_sentences: List[str]) -> float:
        """Calculate content relevance based on word overlap with relevant sentences"""
        if not relevant_sentences:
            return 0.5
        
        # Extract words from user answer
        answer_words = set(re.findall(r'\b\w+\b', user_answer.lower()))
        answer_words = {w for w in answer_words if w not in self.stop_words and len(w) > 3}
        
        if not answer_words:
            return 0.0
        
        # Extract words from relevant sentences
        sentence_words = set()
        for sentence in relevant_sentences:
            words = re.findall(r'\b\w+\b', sentence.lower())
            sentence_words.update([w for w in words if w not in self.stop_words and len(w) > 3])
        
        if not sentence_words:
            return 0.5
        
        # Calculate overlap
        overlap = len(answer_words.intersection(sentence_words))
        relevance_score = overlap / len(answer_words)
        
        return min(relevance_score, 1.0)
    
    def _combine_scores(self, semantic_score: float, keyword_score: float, content_score: float) -> float:
        """Combine different scores into an overall evaluation score"""
        # Weighted combination
        weights = {
            'semantic': 0.4,
            'keyword': 0.3,
            'content': 0.3
        }
        
        overall_score = (
            semantic_score * weights['semantic'] +
            keyword_score * weights['keyword'] +
            content_score * weights['content']
        )
        
        return min(max(overall_score, 0.0), 1.0)
    
    def _generate_feedback(self, overall_score: float, semantic_score: float, 
                          keyword_score: float, content_score: float, user_answer: str) -> str:
        """Generate feedback based on evaluation scores"""
        if overall_score >= 0.8:
            return "Excellent answer! Your response demonstrates strong understanding of the document content."
        elif overall_score >= 0.6:
            return "Good answer! You've captured the main points, but could provide more specific details."
        elif overall_score >= 0.4:
            return "Fair answer. Consider including more relevant concepts and specific information from the document."
        elif overall_score >= 0.2:
            return "Your answer needs improvement. Try to focus more on the specific concepts mentioned in the question."
        else:
            return "Your answer doesn't seem to address the question effectively. Please review the document content."
    
    def _generate_analysis(self, question: Dict, user_answer: str, 
                          relevant_sentences: List[str], overall_score: float) -> str:
        """Generate detailed analysis of the answer"""
        analysis_parts = []
        
        # Answer length analysis
        answer_length = len(user_answer.split())
        if answer_length < 10:
            analysis_parts.append("Your answer is quite brief. Consider providing more detailed explanations.")
        elif answer_length > 100:
            analysis_parts.append("Your answer is comprehensive, which is good for demonstrating understanding.")
        else:
            analysis_parts.append("Your answer has an appropriate length for this type of question.")
        
        # Concept coverage analysis
        expected_concepts = question.get('concepts', [])
        if expected_concepts:
            covered_concepts = []
            for concept in expected_concepts:
                if concept.lower() in user_answer.lower():
                    covered_concepts.append(concept)
            
            if covered_concepts:
                analysis_parts.append(f"You covered these key concepts: {', '.join(covered_concepts)}.")
            else:
                analysis_parts.append("Consider including more of the key concepts mentioned in the question.")
        
        # Overall assessment
        if overall_score >= 0.7:
            analysis_parts.append("Overall, this is a strong response that demonstrates good comprehension.")
        elif overall_score >= 0.5:
            analysis_parts.append("This response shows some understanding but could be more specific.")
        else:
            analysis_parts.append("This response needs significant improvement to demonstrate understanding.")
        
        return " ".join(analysis_parts)
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    def _create_evaluation(self, score: float, feedback: str, analysis: str) -> Dict:
        """Create evaluation result dictionary"""
        return {
            'score': round(score, 2),
            'percentage': round(score * 100, 1),
            'feedback': feedback,
            'analysis': analysis,
            'grade': self._get_grade(score)
        }
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 0.9:
            return "A+"
        elif score >= 0.8:
            return "A"
        elif score >= 0.7:
            return "B+"
        elif score >= 0.6:
            return "B"
        elif score >= 0.5:
            return "C+"
        elif score >= 0.4:
            return "C"
        elif score >= 0.3:
            return "D"
        else:
            return "F" 