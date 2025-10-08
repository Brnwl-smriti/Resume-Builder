"""
Document Summarizer for NeuraDoc
Uses transformers to generate intelligent document summaries
"""

import re
from typing import List
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch


class DocumentSummarizer:
    """Intelligent document summarization using transformers"""
    
    def __init__(self):
        self.model_name = "facebook/bart-large-cnn"
        self.max_length = 150
        self.min_length = 30
        
        # Initialize the summarization pipeline
        try:
            self.summarizer = pipeline(
                "summarization",
                model=self.model_name,
                device=0 if torch.cuda.is_available() else -1
            )
        except Exception as e:
            print(f"Warning: Could not load BART model: {e}")
            self.summarizer = None
    
    def summarize(self, text: str) -> str:
        """
        Generate a summary of the given text
        
        Args:
            text: Input text to summarize
            
        Returns:
            Generated summary (≤150 words)
        """
        if not text or len(text.strip()) < 100:
            return text[:200] + "..." if len(text) > 200 else text
        
        # Clean and prepare text
        cleaned_text = self._preprocess_text(text)
        
        # If text is short enough, return as is
        if len(cleaned_text.split()) <= self.max_length:
            return cleaned_text
        
        try:
            if self.summarizer:
                # Use transformer model for summarization
                summary = self._generate_transformer_summary(cleaned_text)
            else:
                # Fallback to extractive summarization
                summary = self._generate_extractive_summary(cleaned_text)
            
            # Post-process summary
            summary = self._postprocess_summary(summary)
            
            return summary
            
        except Exception as e:
            print(f"Summarization failed: {e}")
            # Fallback to simple truncation
            return self._truncate_text(cleaned_text, self.max_length)
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for summarization"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might interfere
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)]', ' ', text)
        
        # Normalize spacing around punctuation
        text = re.sub(r'\s+([.,;:!?])', r'\1', text)
        
        return text.strip()
    
    def _generate_transformer_summary(self, text: str) -> str:
        """Generate summary using transformer model"""
        # Split text into chunks if too long
        max_chunk_length = 1024
        chunks = self._split_text_into_chunks(text, max_chunk_length)
        
        summaries = []
        for chunk in chunks:
            if len(chunk.split()) < 50:
                summaries.append(chunk)
                continue
            
            result = self.summarizer(
                chunk,
                max_length=self.max_length,
                min_length=self.min_length,
                do_sample=False,
                truncation=True
            )
            
            if result and len(result) > 0:
                summaries.append(result[0]['summary_text'])
        
        # Combine summaries if multiple chunks
        if len(summaries) > 1:
            combined_summary = ' '.join(summaries)
            # Re-summarize if combined summary is too long
            if len(combined_summary.split()) > self.max_length:
                result = self.summarizer(
                    combined_summary,
                    max_length=self.max_length,
                    min_length=self.min_length,
                    do_sample=False,
                    truncation=True
                )
                return result[0]['summary_text'] if result else combined_summary
            return combined_summary
        else:
            return summaries[0] if summaries else text[:200] + "..."
    
    def _generate_extractive_summary(self, text: str) -> str:
        """Generate extractive summary using sentence ranking"""
        sentences = self._split_into_sentences(text)
        
        if len(sentences) <= 3:
            return text
        
        # Simple sentence ranking based on word frequency
        word_freq = self._calculate_word_frequency(text)
        sentence_scores = {}
        
        for i, sentence in enumerate(sentences):
            score = sum(word_freq.get(word.lower(), 0) for word in sentence.split())
            sentence_scores[i] = score / len(sentence.split())
        
        # Select top sentences
        top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
        selected_indices = sorted([idx for idx, _ in top_sentences[:3]])
        
        summary_sentences = [sentences[idx] for idx in selected_indices]
        return ' '.join(summary_sentences)
    
    def _split_text_into_chunks(self, text: str, max_length: int) -> List[str]:
        """Split text into chunks of maximum length"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > max_length:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = [word]
                    current_length = len(word)
                else:
                    # Single word is too long, truncate it
                    chunks.append(word[:max_length])
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _calculate_word_frequency(self, text: str) -> dict:
        """Calculate word frequency in text"""
        words = re.findall(r'\b\w+\b', text.lower())
        freq = {}
        for word in words:
            if len(word) > 2:  # Skip very short words
                freq[word] = freq.get(word, 0) + 1
        return freq
    
    def _postprocess_summary(self, summary: str) -> str:
        """Post-process the generated summary"""
        # Ensure summary doesn't exceed max length
        if len(summary.split()) > self.max_length:
            summary = self._truncate_text(summary, self.max_length)
        
        # Clean up formatting
        summary = re.sub(r'\s+', ' ', summary)
        summary = summary.strip()
        
        # Ensure it ends with proper punctuation
        if summary and not summary[-1] in '.!?':
            summary += '.'
        
        return summary
    
    def _truncate_text(self, text: str, max_words: int) -> str:
        """Truncate text to maximum number of words"""
        words = text.split()
        if len(words) <= max_words:
            return text
        
        truncated = ' '.join(words[:max_words])
        if not truncated.endswith(('.', '!', '?')):
            truncated += '...'
        
        return truncated 