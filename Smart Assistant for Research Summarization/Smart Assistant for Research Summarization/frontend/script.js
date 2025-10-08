/**
 * NeuraDoc - Frontend JavaScript
 * Handles all interactive functionality and API communication
 */

class NeuraDoc {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.currentMode = 'ask';
        this.challengeQuestions = [];
        this.isProcessing = false;
        
        this.initializeElements();
        this.bindEvents();
        this.initializeAnimations();
    }

    // Initialize DOM elements
    initializeElements() {
        this.elements = {
            // Upload
            uploadArea: document.getElementById('uploadArea'),
            fileInput: document.getElementById('fileInput'),
            uploadBtn: document.getElementById('uploadBtn'),
            uploadProgress: document.getElementById('uploadProgress'),
            progressFill: document.getElementById('progressFill'),
            progressText: document.getElementById('progressText'),
            
            // Sections
            uploadSection: document.getElementById('uploadSection'),
            summarySection: document.getElementById('summarySection'),
            modeSection: document.getElementById('modeSection'),
            askSection: document.getElementById('askSection'),
            challengeSection: document.getElementById('challengeSection'),
            
            // Summary
            summaryContent: document.getElementById('summaryContent'),
            documentInfo: document.getElementById('documentInfo'),
            
            // Mode tabs
            modeTabs: document.querySelectorAll('.mode-tab'),
            
            // Chat
            chatMessages: document.getElementById('chatMessages'),
            questionInput: document.getElementById('questionInput'),
            sendBtn: document.getElementById('sendBtn'),
            
            // Challenge
            generateChallengeBtn: document.getElementById('generateChallengeBtn'),
            challengeQuestions: document.getElementById('challengeQuestions'),
            questionList: document.getElementById('questionList'),
            challengeResults: document.getElementById('challengeResults'),
            resultsContainer: document.getElementById('resultsContainer'),
            
            // UI
            resetBtn: document.getElementById('resetBtn'),
            infoBtn: document.getElementById('infoBtn'),
            infoModal: document.getElementById('infoModal'),
            closeInfoModal: document.getElementById('closeInfoModal'),
            loadingOverlay: document.getElementById('loadingOverlay'),
            loadingText: document.getElementById('loadingText'),
            aiAvatar: document.getElementById('aiAvatar')
        };
    }

    // Bind event listeners
    bindEvents() {
        // Upload events
        this.elements.uploadBtn.addEventListener('click', () => this.elements.fileInput.click());
        this.elements.fileInput.addEventListener('change', (e) => this.handleFileUpload(e));
        this.elements.uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.elements.uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.elements.uploadArea.addEventListener('drop', (e) => this.handleDrop(e));
        
        // Mode switching
        this.elements.modeTabs.forEach(tab => {
            tab.addEventListener('click', () => this.switchMode(tab.dataset.mode));
        });
        
        // Chat events
        this.elements.sendBtn.addEventListener('click', () => this.sendQuestion());
        this.elements.questionInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendQuestion();
            }
        });
        
        // Challenge events
        this.elements.generateChallengeBtn.addEventListener('click', () => this.generateChallenge());
        
        // UI events
        this.elements.resetBtn.addEventListener('click', () => this.resetSession());
        this.elements.infoBtn.addEventListener('click', () => this.showInfoModal());
        this.elements.closeInfoModal.addEventListener('click', () => this.hideInfoModal());
        this.elements.infoModal.addEventListener('click', (e) => {
            if (e.target === this.elements.infoModal) this.hideInfoModal();
        });
        
        // AI Avatar
        this.elements.aiAvatar.addEventListener('click', () => this.toggleAIAvatar());
    }

    // Initialize animations and effects
    initializeAnimations() {
        // Add typing animation to AI messages
        this.addTypingAnimation();
        
        // Initialize AI avatar pulse
        this.initializeAIAvatar();
        
        // Add smooth scrolling to chat
        this.elements.chatMessages.addEventListener('scroll', this.throttle(() => {
            // Smooth scroll behavior
        }, 100));
    }

    // File upload handling
    async handleFileUpload(event) {
        const file = event.target.files[0];
        if (file) {
            await this.processFile(file);
        }
    }

    handleDragOver(event) {
        event.preventDefault();
        this.elements.uploadArea.classList.add('dragover');
    }

    handleDragLeave(event) {
        event.preventDefault();
        this.elements.uploadArea.classList.remove('dragover');
    }

    handleDrop(event) {
        event.preventDefault();
        this.elements.uploadArea.classList.remove('dragover');
        
        const files = event.dataTransfer.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }

    async processFile(file) {
        // Validate file type
        if (!this.isValidFileType(file)) {
            this.showNotification('Please upload a PDF or TXT file.', 'error');
            return;
        }

        // Validate file size (16MB limit)
        if (file.size > 16 * 1024 * 1024) {
            this.showNotification('File size must be less than 16MB.', 'error');
            return;
        }

        this.showLoading('Processing document...');
        this.showUploadProgress();

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/api/upload', {
                method: 'POST',
                headers: {
                    'X-Session-ID': this.sessionId
                },
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                this.hideLoading();
                this.hideUploadProgress();
                this.showDocumentSummary(result);
                this.showNotification('Document uploaded successfully!', 'success');
            } else {
                throw new Error(result.error || 'Upload failed');
            }
        } catch (error) {
            this.hideLoading();
            this.hideUploadProgress();
            this.showNotification(`Upload failed: ${error.message}`, 'error');
        }
    }

    isValidFileType(file) {
        const validTypes = ['application/pdf', 'text/plain'];
        const validExtensions = ['.pdf', '.txt'];
        
        return validTypes.includes(file.type) || 
               validExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
    }

    showUploadProgress() {
        this.elements.uploadProgress.style.display = 'block';
        this.elements.uploadArea.querySelector('.upload-content').style.display = 'none';
        
        // Simulate progress
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 90) progress = 90;
            
            this.elements.progressFill.style.width = `${progress}%`;
            this.elements.progressText.textContent = this.getProgressText(progress);
            
            if (progress >= 90) {
                clearInterval(interval);
            }
        }, 200);
    }

    hideUploadProgress() {
        this.elements.uploadProgress.style.display = 'none';
        this.elements.uploadArea.querySelector('.upload-content').style.display = 'block';
        this.elements.progressFill.style.width = '0%';
    }

    getProgressText(progress) {
        if (progress < 30) return 'Parsing document...';
        if (progress < 60) return 'Analyzing content...';
        if (progress < 90) return 'Generating summary...';
        return 'Finalizing...';
    }

    showDocumentSummary(result) {
        this.elements.summaryContent.innerHTML = `
            <p>${result.summary}</p>
        `;
        
        this.elements.documentInfo.innerHTML = `
            <span>📄 ${result.filename}</span>
            <span>📊 ${result.word_count} words</span>
            <span>🆔 ${result.session_id}</span>
        `;
        
        this.elements.summarySection.style.display = 'block';
        this.elements.modeSection.style.display = 'block';
        this.elements.uploadSection.style.display = 'none';
        
        // Show ask mode by default
        this.switchMode('ask');
    }

    // Mode switching
    switchMode(mode) {
        this.currentMode = mode;
        
        // Update tab states
        this.elements.modeTabs.forEach(tab => {
            tab.classList.toggle('active', tab.dataset.mode === mode);
        });
        
        // Show/hide sections
        this.elements.askSection.style.display = mode === 'ask' ? 'flex' : 'none';
        this.elements.challengeSection.style.display = mode === 'challenge' ? 'block' : 'none';
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // Chat functionality
    async sendQuestion() {
        const question = this.elements.questionInput.value.trim();
        if (!question) return;

        if (this.isProcessing) return;
        this.isProcessing = true;

        // Add user message
        this.addMessage(question, 'user');
        this.elements.questionInput.value = '';

        // Show typing indicator
        const typingMessage = this.addTypingIndicator();

        try {
            const response = await fetch('/api/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Session-ID': this.sessionId
                },
                body: JSON.stringify({ question })
            });

            const result = await response.json();

            // Remove typing indicator
            typingMessage.remove();

            if (result.success) {
                this.addAIResponse(result.answer, result.references, result.source_sentences);
            } else {
                throw new Error(result.error || 'Failed to get answer');
            }
        } catch (error) {
            typingMessage.remove();
            this.addMessage(`Sorry, I encountered an error: ${error.message}`, 'ai');
        } finally {
            this.isProcessing = false;
        }
    }

    addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = type === 'user' ? '👤' : '🤖';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        if (type === 'ai' && typeof content === 'object') {
            // Handle AI response with references
            messageContent.innerHTML = `
                <p>${content.answer}</p>
                ${content.references ? `<div class="reference">${content.references.join('<br>')}</div>` : ''}
            `;
        } else {
            messageContent.innerHTML = `<p>${content}</p>`;
        }
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        return messageDiv;
    }

    addAIResponse(answer, references, sourceSentences) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message ai-message';
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = '🤖';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        let referencesHtml = '';
        if (references && references.length > 0) {
            referencesHtml = `<div class="reference">${references.join('<br>')}</div>`;
        }
        
        messageContent.innerHTML = `
            <p>${answer}</p>
            ${referencesHtml}
        `;
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Add typing animation
        this.addTypingAnimationToMessage(messageDiv);
    }

    addTypingIndicator() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message ai-message typing-indicator';
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = '🤖';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.innerHTML = '<p>Thinking...</p>';
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        return messageDiv;
    }

    // Challenge functionality
    async generateChallenge() {
        if (this.isProcessing) return;
        this.isProcessing = true;

        this.showLoading('Generating challenge questions...');

        try {
            const response = await fetch('/api/challenge', {
                method: 'POST',
                headers: {
                    'X-Session-ID': this.sessionId
                }
            });

            const result = await response.json();

            if (result.success) {
                this.challengeQuestions = result.questions;
                this.displayChallengeQuestions();
            } else {
                throw new Error(result.error || 'Failed to generate questions');
            }
        } catch (error) {
            this.showNotification(`Failed to generate questions: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
            this.isProcessing = false;
        }
    }

    displayChallengeQuestions() {
        this.elements.questionList.innerHTML = '';
        
        this.challengeQuestions.forEach((question, index) => {
            const questionDiv = document.createElement('div');
            questionDiv.className = 'question-item';
            questionDiv.innerHTML = `
                <div class="question-text">${index + 1}. ${question.question}</div>
                <textarea class="answer-input" placeholder="Enter your answer here..." data-question-index="${index}"></textarea>
                <div class="question-actions">
                    <button class="btn-primary evaluate-btn" data-question-index="${index}">
                        <span class="btn-icon">✅</span>
                        Evaluate Answer
                    </button>
                </div>
            `;
            
            this.elements.questionList.appendChild(questionDiv);
        });
        
        this.elements.challengeQuestions.style.display = 'block';
        
        // Bind evaluate buttons
        document.querySelectorAll('.evaluate-btn').forEach(btn => {
            btn.addEventListener('click', () => this.evaluateAnswer(btn.dataset.questionIndex));
        });
    }

    async evaluateAnswer(questionIndex) {
        const answerInput = document.querySelector(`textarea[data-question-index="${questionIndex}"]`);
        const answer = answerInput.value.trim();
        
        if (!answer) {
            this.showNotification('Please enter an answer before evaluating.', 'error');
            return;
        }

        this.showLoading('Evaluating your answer...');

        try {
            const response = await fetch('/api/evaluate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Session-ID': this.sessionId
                },
                body: JSON.stringify({
                    question_index: parseInt(questionIndex),
                    answer: answer
                })
            });

            const result = await response.json();

            if (result.success) {
                this.displayEvaluationResult(questionIndex, result.evaluation);
            } else {
                throw new Error(result.error || 'Evaluation failed');
            }
        } catch (error) {
            this.showNotification(`Evaluation failed: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    displayEvaluationResult(questionIndex, evaluation) {
        const resultDiv = document.createElement('div');
        resultDiv.className = 'result-item';
        resultDiv.innerHTML = `
            <div class="result-score">
                <div class="score-circle">${evaluation.grade}</div>
                <div class="score-details">
                    <div class="score-percentage">${evaluation.percentage}%</div>
                    <div class="score-grade">Grade: ${evaluation.grade}</div>
                </div>
            </div>
            <div class="result-feedback">${evaluation.feedback}</div>
            <div class="result-analysis">${evaluation.analysis}</div>
        `;
        
        this.elements.resultsContainer.appendChild(resultDiv);
        this.elements.challengeResults.style.display = 'block';
        
        // Scroll to results
        this.elements.challengeResults.scrollIntoView({ behavior: 'smooth' });
    }

    // Session management
    resetSession() {
        if (confirm('Are you sure you want to reset the session? This will clear all uploaded documents and conversation history.')) {
            fetch('/api/reset', {
                method: 'POST',
                headers: {
                    'X-Session-ID': this.sessionId
                }
            }).then(() => {
                this.sessionId = this.generateSessionId();
                this.resetUI();
                this.showNotification('Session reset successfully!', 'success');
            }).catch(error => {
                this.showNotification(`Reset failed: ${error.message}`, 'error');
            });
        }
    }

    resetUI() {
        // Reset all sections
        this.elements.uploadSection.style.display = 'flex';
        this.elements.summarySection.style.display = 'none';
        this.elements.modeSection.style.display = 'none';
        this.elements.askSection.style.display = 'none';
        this.elements.challengeSection.style.display = 'none';
        
        // Clear content
        this.elements.chatMessages.innerHTML = `
            <div class="message ai-message">
                <div class="message-avatar">🤖</div>
                <div class="message-content">
                    <p>Hello! I've analyzed your document. Ask me anything about its content, and I'll provide grounded answers with references.</p>
                </div>
            </div>
        `;
        
        this.elements.questionList.innerHTML = '';
        this.elements.resultsContainer.innerHTML = '';
        this.elements.challengeQuestions.style.display = 'none';
        this.elements.challengeResults.style.display = 'none';
        
        // Reset file input
        this.elements.fileInput.value = '';
        
        // Reset mode
        this.currentMode = 'ask';
        this.elements.modeTabs.forEach(tab => {
            tab.classList.toggle('active', tab.dataset.mode === 'ask');
        });
    }

    // UI utilities
    showLoading(message = 'Processing...') {
        this.elements.loadingText.textContent = message;
        this.elements.loadingOverlay.classList.add('active');
    }

    hideLoading() {
        this.elements.loadingOverlay.classList.remove('active');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            padding: 12px 24px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 4000;
            animation: slideIn 0.3s ease;
        `;
        
        if (type === 'success') {
            notification.style.background = 'linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%)';
        } else if (type === 'error') {
            notification.style.background = 'linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%)';
        } else {
            notification.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
        }
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    showInfoModal() {
        this.elements.infoModal.classList.add('active');
    }

    hideInfoModal() {
        this.elements.infoModal.classList.remove('active');
    }

    toggleAIAvatar() {
        this.elements.aiAvatar.style.transform = this.elements.aiAvatar.style.transform === 'scale(1.2)' 
            ? 'scale(1)' 
            : 'scale(1.2)';
    }

    // Animation utilities
    addTypingAnimation() {
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(-50%) translateY(-100%); opacity: 0; }
                to { transform: translateX(-50%) translateY(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(-50%) translateY(0); opacity: 1; }
                to { transform: translateX(-50%) translateY(-100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }

    addTypingAnimationToMessage(messageDiv) {
        const textElement = messageDiv.querySelector('p');
        const originalText = textElement.textContent;
        textElement.textContent = '';
        
        let i = 0;
        const typeWriter = () => {
            if (i < originalText.length) {
                textElement.textContent += originalText.charAt(i);
                i++;
                setTimeout(typeWriter, 30);
            }
        };
        typeWriter();
    }

    initializeAIAvatar() {
        // Add pulse animation to AI avatar
        setInterval(() => {
            this.elements.aiAvatar.style.transform = 'scale(1.05)';
            setTimeout(() => {
                this.elements.aiAvatar.style.transform = 'scale(1)';
            }, 200);
        }, 3000);
    }

    scrollToBottom() {
        setTimeout(() => {
            this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
        }, 100);
    }

    // Utility functions
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.neuraDoc = new NeuraDoc();
    console.log('🌌 NeuraDoc initialized successfully!');
}); 