"""
Challenge Generator for NeuraDoc
Generates logic-based questions from document content
"""

import re
import random
from typing import List, Dict
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords


class ChallengeGenerator:
    """Generates logic-based challenge questions from document content"""
    
    def __init__(self):
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            nltk.download('punkt_tab')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        self.stop_words = set(stopwords.words('english'))
        self.question_templates = [
            "What is the main argument presented about {topic}?",
            "How does the document explain the relationship between {concept1} and {concept2}?",
            "What evidence does the author provide to support the claim about {topic}?",
            "According to the document, what are the key factors that influence {concept}?",
            "What conclusion can be drawn about {topic} based on the information provided?",
            "How does the document define or describe {concept}?",
            "What are the implications of {concept} as discussed in the document?",
            "Based on the document, what is the significance of {topic}?",
            "What are the main differences between {concept1} and {concept2} as described?",
            "How does the author justify their position on {topic}?"
        ]
    
    def generate_questions(self, document_text: str) -> List[Dict]:
        """
        Generate 3 logic-based questions from document content
        
        Args:
            document_text: The document text to analyze
            
        Returns:
            List of question dictionaries with question text and expected concepts
        """
        if not document_text or len(document_text.strip()) < 100:
            return self._generate_fallback_questions()
        
        try:
            # Extract key concepts and topics
            key_concepts = self._extract_key_concepts(document_text)
            
            if len(key_concepts) < 2:
                return self._generate_fallback_questions()
            
            # Generate questions
            questions = []
            used_concepts = set()
            
            for i in range(3):
                question_data = self._generate_single_question(
                    document_text, key_concepts, used_concepts
                )
                if question_data:
                    questions.append(question_data)
                    used_concepts.update(question_data.get('concepts', []))
            
            # If we couldn't generate enough questions, add fallbacks
            while len(questions) < 3:
                fallback = self._generate_fallback_question(document_text)
                questions.append(fallback)
            
            return questions[:3]
            
        except Exception as e:
            print(f"Question generation failed: {e}")
            return self._generate_fallback_questions()
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts and topics from the document"""
        # Clean text
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = word_tokenize(text)
        
        # Remove stop words and short words
        words = [word for word in words if word not in self.stop_words and len(word) > 3]
        
        # Count word frequency
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get most frequent words
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        key_concepts = [word for word, freq in sorted_words[:20] if freq > 2]
        
        return key_concepts
    
    def _generate_single_question(self, text: str, key_concepts: List[str], used_concepts: set) -> Dict:
        """Generate a single question using available concepts"""
        if len(key_concepts) < 2:
            return None
        
        # Select concepts that haven't been used
        available_concepts = [c for c in key_concepts if c not in used_concepts]
        
        if len(available_concepts) < 2:
            # Reuse some concepts if necessary
            available_concepts = key_concepts[:2]
        
        # Select random concepts
        selected_concepts = random.sample(available_concepts, min(2, len(available_concepts)))
        
        # Select a question template
        template = random.choice(self.question_templates)
        
        # Fill the template
        if len(selected_concepts) >= 2:
            question_text = template.format(
                topic=selected_concepts[0],
                concept1=selected_concepts[0],
                concept2=selected_concepts[1],
                concept=selected_concepts[0]
            )
        else:
            question_text = template.format(
                topic=selected_concepts[0],
                concept1=selected_concepts[0],
                concept2=selected_concepts[0],
                concept=selected_concepts[0]
            )
        
        return {
            'question': question_text,
            'concepts': selected_concepts,
            'type': 'logic',
            'difficulty': 'medium'
        }
    
    def _generate_fallback_questions(self) -> List[Dict]:
        """Generate fallback questions when document analysis fails"""
        return [
            {
                'question': 'What is the main topic discussed in this document?',
                'concepts': ['main topic', 'document content'],
                'type': 'comprehension',
                'difficulty': 'easy'
            },
            {
                'question': 'What are the key points or arguments presented in the document?',
                'concepts': ['key points', 'arguments'],
                'type': 'analysis',
                'difficulty': 'medium'
            },
            {
                'question': 'What conclusions or implications can be drawn from the information provided?',
                'concepts': ['conclusions', 'implications'],
                'type': 'synthesis',
                'difficulty': 'hard'
            }
        ]
    
    def _generate_fallback_question(self, text: str) -> Dict:
        """Generate a single fallback question"""
        sentences = sent_tokenize(text)
        if not sentences:
            return self._generate_fallback_questions()[0]
        
        # Extract a key sentence
        key_sentence = random.choice(sentences[:10])  # Use first 10 sentences
        
        # Create a question about the sentence
        question_text = f"What does the document state about the following: '{key_sentence[:100]}...'?"
        
        return {
            'question': question_text,
            'concepts': ['document content', 'key information'],
            'type': 'comprehension',
            'difficulty': 'easy'
        }
    
    def _extract_named_entities(self, text: str) -> List[str]:
        """Extract named entities from text (simplified version)"""
        # Simple pattern matching for common named entities
        patterns = [
            r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # Proper nouns
            r'\b[A-Z]{2,}\b',  # Acronyms
            r'\b\d{4}\b',  # Years
        ]
        
        entities = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            entities.extend(matches)
        
        return list(set(entities))
    
    def _identify_relationships(self, text: str) -> List[Dict]:
        """Identify relationships between concepts in the text"""
        relationships = []
        
        # Look for relationship indicators
        relationship_indicators = [
            'because', 'therefore', 'however', 'although', 'while',
            'leads to', 'results in', 'causes', 'affects', 'influences',
            'related to', 'connected with', 'depends on'
        ]
        
        sentences = sent_tokenize(text)
        for sentence in sentences:
            for indicator in relationship_indicators:
                if indicator in sentence.lower():
                    # Extract concepts around the indicator
                    words = word_tokenize(sentence)
                    try:
                        indicator_pos = [i for i, word in enumerate(words) if indicator in word.lower()][0]
                        
                        # Get words before and after the indicator
                        before = ' '.join(words[max(0, indicator_pos-3):indicator_pos])
                        after = ' '.join(words[indicator_pos+1:indicator_pos+4])
                        
                        if before and after:
                            relationships.append({
                                'concept1': before,
                                'relationship': indicator,
                                'concept2': after,
                                'sentence': sentence
                            })
                    except:
                        continue
        
        return relationships 