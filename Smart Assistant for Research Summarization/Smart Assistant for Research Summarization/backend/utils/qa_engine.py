"""
Question-Answering Engine for NeuraDoc
Provides document-grounded answers with semantic search and references
"""

import re
import numpy as np
from typing import List, Tuple, Dict
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline
import torch


class QAEngine:
    """Question-answering engine with semantic search and document grounding"""
    
    def __init__(self):
        # Initialize sentence transformer for semantic search
        try:
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Warning: Could not load sentence transformer: {e}")
            self.embedder = None
        
        # Initialize QA pipeline
        try:
            self.qa_pipeline = pipeline(
                "question-answering",
                model="deepset/roberta-base-squad2",
                device=0 if torch.cuda.is_available() else -1
            )
        except Exception as e:
            print(f"Warning: Could not load QA model: {e}")
            self.qa_pipeline = None
    
    def answer_question(self, question: str, document_text: str) -> Tuple[str, List[str], List[str]]:
        """
        Answer a question based on document content with references
        
        Args:
            question: User's question
            document_text: Full document text
            
        Returns:
            Tuple of (answer, references, source_sentences)
        """
        if not question or not document_text:
            return "I cannot answer this question without sufficient context.", [], []
        
        try:
            # Split document into chunks
            chunks = self._split_document_into_chunks(document_text)
            
            if not chunks:
                return "The document appears to be empty or could not be processed.", [], []
            
            # Find most relevant chunks using semantic search
            relevant_chunks = self._find_relevant_chunks(question, chunks)
            
            if not relevant_chunks:
                return "I couldn't find relevant information in the document to answer your question.", [], []
            
            # Generate answer using QA model or fallback
            if self.qa_pipeline:
                answer, source_sentences = self._generate_qa_answer(question, relevant_chunks)
            else:
                answer, source_sentences = self._generate_fallback_answer(question, relevant_chunks)
            
            # Generate references
            references = self._generate_references(source_sentences, document_text)
            
            return answer, references, source_sentences
            
        except Exception as e:
            print(f"QA processing failed: {e}")
            return "I encountered an error while processing your question. Please try again.", [], []
    
    def _split_document_into_chunks(self, text: str, chunk_size: int = 500) -> List[str]:
        """Split document into overlapping chunks"""
        sentences = self._split_into_sentences(text)
        chunks = []
        
        for i in range(0, len(sentences), chunk_size // 2):  # 50% overlap
            chunk = ' '.join(sentences[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # More sophisticated sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    def _find_relevant_chunks(self, question: str, chunks: List[str]) -> List[str]:
        """Find most relevant chunks using semantic similarity"""
        if not self.embedder:
            # Fallback: return first few chunks
            return chunks[:3]
        
        try:
            # Encode question and chunks
            question_embedding = self.embedder.encode([question])
            chunk_embeddings = self.embedder.encode(chunks)
            
            # Calculate similarities
            similarities = cosine_similarity(question_embedding, chunk_embeddings)[0]
            
            # Get top 3 most similar chunks
            top_indices = np.argsort(similarities)[::-1][:3]
            relevant_chunks = [chunks[i] for i in top_indices if similarities[i] > 0.3]
            
            return relevant_chunks if relevant_chunks else chunks[:2]
            
        except Exception as e:
            print(f"Semantic search failed: {e}")
            return chunks[:3]
    
    def _generate_qa_answer(self, question: str, chunks: List[str]) -> Tuple[str, List[str]]:
        """Generate answer using QA pipeline"""
        best_answer = ""
        best_score = 0
        source_sentences = []
        
        for chunk in chunks:
            try:
                result = self.qa_pipeline(
                    question=question,
                    context=chunk,
                    max_answer_len=100,
                    handle_impossible_answer=True
                )
                
                if result['score'] > best_score and result['answer']:
                    best_score = result['score']
                    best_answer = result['answer']
                    
                    # Extract source sentence containing the answer
                    answer_start = result['start']
                    answer_end = result['end']
                    
                    # Find the sentence containing the answer
                    sentences = self._split_into_sentences(chunk)
                    for sentence in sentences:
                        if best_answer.lower() in sentence.lower():
                            source_sentences.append(sentence)
                            break
                    
            except Exception as e:
                print(f"QA pipeline failed for chunk: {e}")
                continue
        
        if not best_answer:
            return self._generate_fallback_answer(question, chunks)
        
        return best_answer, source_sentences
    
    def _generate_fallback_answer(self, question: str, chunks: List[str]) -> Tuple[str, List[str]]:
        """Generate answer using keyword matching and sentence extraction"""
        question_words = set(re.findall(r'\b\w+\b', question.lower()))
        question_words = {w for w in question_words if len(w) > 3}  # Filter short words
        
        best_sentences = []
        sentence_scores = []
        
        for chunk in chunks:
            sentences = self._split_into_sentences(chunk)
            
            for sentence in sentences:
                sentence_words = set(re.findall(r'\b\w+\b', sentence.lower()))
                sentence_words = {w for w in sentence_words if len(w) > 3}
                
                # Calculate word overlap
                overlap = len(question_words.intersection(sentence_words))
                if overlap > 0:
                    score = overlap / len(question_words)
                    sentence_scores.append((score, sentence))
        
        # Sort by score and get top sentences
        sentence_scores.sort(reverse=True)
        top_sentences = [sentence for score, sentence in sentence_scores[:2] if score > 0.2]
        
        if top_sentences:
            # Combine sentences into an answer
            answer = ' '.join(top_sentences)
            if len(answer) > 300:
                answer = answer[:300] + "..."
            return answer, top_sentences
        else:
            # No good matches found
            return "I couldn't find a specific answer to your question in the document.", []
    
    def _generate_references(self, source_sentences: List[str], document_text: str) -> List[str]:
        """Generate reference citations for source sentences"""
        references = []
        
        for sentence in source_sentences:
            # Find approximate location in document
            try:
                # Find the sentence in the document
                start_pos = document_text.find(sentence)
                if start_pos != -1:
                    # Calculate approximate paragraph number
                    text_before = document_text[:start_pos]
                    paragraphs = text_before.split('\n\n')
                    paragraph_num = len(paragraphs)
                    
                    # Calculate approximate sentence number in paragraph
                    paragraph_text = paragraphs[-1] if paragraphs else ""
                    sentences_in_paragraph = len(self._split_into_sentences(paragraph_text))
                    
                    reference = f"Based on paragraph {paragraph_num}, sentence {sentences_in_paragraph + 1}"
                    references.append(reference)
                else:
                    references.append("Based on document content")
            except:
                references.append("Based on document content")
        
        return references
    
    def get_conversation_context(self, question: str, document_text: str) -> Dict:
        """Get context information for the question"""
        chunks = self._split_document_into_chunks(document_text)
        relevant_chunks = self._find_relevant_chunks(question, chunks)
        
        return {
            'question': question,
            'relevant_chunks': relevant_chunks,
            'total_chunks': len(chunks),
            'document_length': len(document_text)
        } 