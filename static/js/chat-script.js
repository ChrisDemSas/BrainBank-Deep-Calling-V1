class ChatInterface {

    // The ChatInterface class which aims to provide the functions for the Chatting functions.
    // The Features are:
        // 1. Obtain questions from the backend
        // 2. Send responses to the backend
        // 3. Navigate between results
        // 4. Obtain results from the evaluation

    constructor () { 
        this.questionCount = -1; // First question is: Type Start
        this.maxQuestions = 13; //Change this later!
        this.chatMessages = document.getElementById("chat-messages");
        this.sendBtn = document.getElementById("send-btn");
        this.viewResults = document.getElementById("view-results");
        this.response = document.querySelector("textarea");
        this.inputContainer = document.getElementById("input-container")

        this.initializeEventListeners();
        this.startChat();
    }

    // Initialize the Event Listeners: clicking, Enter Key
    initializeEventListeners () {
        this.sendBtn.addEventListener('click', () => this.handleUserInput());
        this.response.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleUserInput();
            }
        });
        this.viewResults.addEventListener('click', () => this.showResults())
    }

    // Start the Chat: Remove the name of the inputContainer so that people can start chatting
    async startChat () {
        this.addMessage("Type 'Start' to start the interview.");
        this.inputContainer.classList.remove('hidden') 
    }

    // Handle User Input
    handleUserInput () {
        const userInput = this.response.value.trim();
        if (!userInput) return;

        this.addMessage(userInput, 'user');
        this.response.value = '';
        this.questionCount ++;

        if (this.questionCount < this.maxQuestions) {
            setTimeout(() => { // Get the next question
                this.addMessage("Analyzing Response...")
                    fetch("/get_response", {
                        method: "POST",
                        headers: {"Content-Type": "application/x-www-form-urlencoded" },
                        body: `message=${userInput}`
                    })
                    .then(response => response.json())
                    .then(data => {
                        this.addMessage(data.question)
                    })
            }, 1000); 
        } else {
            this.inputContainer.classList.add('hidden');
            this.viewResults.classList.add('visible');
        }
        }
    
    addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        messageDiv.textContent = content;
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    // Results Showcase

    async showResults () {
        const results = await this.fetchResults();
        
        // Create the base container structure
        document.querySelector('.container').innerHTML = `
            <div class="sidebar">
                <div class="logo">
                    <div class="brain-bank">■ Brain Bank</div>
                    <div class="deep-calling">└ Deep Calling</div>
                </div>
                
                <div class="info-section">
                    <h3>Information</h3>
                    <p>The Deep Calling feature aims to match provide quality matches between the candidate and any impact ventures. Our AI agent will do its best to interview you, so please answer as wholly as possible!</p>
                    
                    <p class="feedback-note">As our AI is still a work in progress, we appreciate your feedback here:</p>
                    <button class="feedback-btn">Feedback</button>
                </div>
                
                <div class="user-info">■ John Doe</div>
            </div>
            <div class="results-page">
                <h2>■ Thank you for answering the questions!</h2>
                
                <div class="results-container">
                    <div class="navigation-arrows">
                        <button class="nav-arrow prev-btn">←</button>
                        <button class="nav-arrow next-btn">→</button>
                    </div>
                    <div class="results-content"></div>
                    <div class="results-pagination"></div>
                </div>
            </div>
        `;

        // Initialize the results display
        this.currentResultIndex = 0;
        this.results = results;
        
        // Create result cards
        const resultsContent = document.querySelector('.results-content');
        results.forEach((result, index) => {
            const resultCard = document.createElement('div');
            resultCard.className = `result-card ${index === 0 ? 'active' : ''}`;
            resultCard.innerHTML = `
                <div class="presage-section">
                    <h3>${result.name}</h3>
                    <p>${result.values_summary}</p>
                    <p>${result.future_goals_and_interests}</p>
                    <button class="connect-btn">Connect</button>
                </div>
            `;
            resultsContent.appendChild(resultCard);
        });

        // Create pagination indicators
        const paginationContainer = document.querySelector('.results-pagination');
        results.forEach((_, index) => {
            const indicator = document.createElement('div');
            indicator.className = `page-indicator ${index === 0 ? 'active' : ''}`;
            paginationContainer.appendChild(indicator);
        });

        // Add event listeners for navigation
        const prevBtn = document.querySelector('.prev-btn');
        const nextBtn = document.querySelector('.next-btn');
        
        prevBtn.addEventListener('click', () => this.navigateResults('prev'));
        nextBtn.addEventListener('click', () => this.navigateResults('next'));
        
        // Update navigation state
        this.updateNavigation();
    }

    async fetchResults() {
        // Make the API Call to Flask

        const response = await fetch("/get_match", {
            method: "GET",
            headers: {
                "Content-Type": "application/json"
            }
            });

        const results = response.json();
        return results;
    }

    navigateResults(direction) {
        const cards = document.querySelectorAll('.result-card');
        const indicators = document.querySelectorAll('.page-indicator');
        
        // Remove active class from current card and indicator
        cards[this.currentResultIndex].classList.remove('active');
        indicators[this.currentResultIndex].classList.remove('active');
        
        // Update current index
        if (direction === 'next') {
            this.currentResultIndex = Math.min(this.currentResultIndex + 1, this.results.length - 1);
        } else {
            this.currentResultIndex = Math.max(this.currentResultIndex - 1, 0);
        }
        
        // Add active class to new current card and indicator
        cards[this.currentResultIndex].classList.add('active');
        indicators[this.currentResultIndex].classList.add('active');
        
        // Update navigation state
        this.updateNavigation();
    }

    updateNavigation() {
        const prevBtn = document.querySelector('.prev-btn');
        const nextBtn = document.querySelector('.next-btn');
        
        // Update prev button state
        if (this.currentResultIndex === 0) {
            prevBtn.classList.add('disabled');
        } else {
            prevBtn.classList.remove('disabled');
        }
        
        // Update next button state
        if (this.currentResultIndex === this.results.length - 1) {
            nextBtn.classList.add('disabled');
        } else {
            nextBtn.classList.remove('disabled');
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ChatInterface();
}
)