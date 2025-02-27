document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const questionText = document.getElementById('question-text');
    const optionsContainer = document.getElementById('options-container');
    const feedbackContainer = document.getElementById('feedback-container');
    const resultMessage = document.getElementById('result-message');
    const explanation = document.getElementById('explanation');
    const sourceLink = document.getElementById('source-link');
    const nextButton = document.getElementById('next-button');
    const questionNumber = document.getElementById('question-number');
    const totalQuestions = document.getElementById('total-questions');

    // State
    let selectedOption = null;

    // Initialize quiz
    loadQuestion();

    // Event listeners
    nextButton.addEventListener('click', function() {
        feedbackContainer.classList.add('hidden');
        loadQuestion();
    });

    // Functions
    function loadQuestion() {
        fetch('/get_question')
            .then(response => response.json())
            .then(data => {
                if (data.complete) {
                    window.location.href = '/results';
                    return;
                }

                // Update question text and number
                questionText.textContent = data.question;
                questionNumber.textContent = `Question ${data.questionNumber}`;
                totalQuestions.textContent = data.totalQuestions;

                // Create option elements
                optionsContainer.innerHTML = '';
                data.options.forEach((option, index) => {
                    const optionElement = document.createElement('div');
                    optionElement.className = 'option';
                    optionElement.textContent = option;
                    optionElement.setAttribute('data-index', index);

                    optionElement.addEventListener('click', function() {
                        if (feedbackContainer.classList.contains('hidden')) {
                            selectOption(this);
                        }
                    });

                    optionsContainer.appendChild(optionElement);
                });
            })
            .catch(error => {
                console.error('Error loading question:', error);
                questionText.textContent = 'Error loading question. Please try again.';
            });
    }

    function selectOption(optionElement) {
        // Clear previous selection
        const options = document.querySelectorAll('.option');
        options.forEach(opt => opt.classList.remove('selected'));

        // Mark current selection
        optionElement.classList.add('selected');
        selectedOption = parseInt(optionElement.getAttribute('data-index'));

        // Submit answer
        submitAnswer(selectedOption);
    }

    function submitAnswer(answerIndex) {
        fetch('/submit_answer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ answer: answerIndex })
        })
        .then(response => response.json())
        .then(data => {
            // Show feedback
            const options = document.querySelectorAll('.option');

            // Mark correct and incorrect answers
            options.forEach((opt, index) => {
                if (index === data.correctAnswer) {
                    opt.classList.add('correct');
                } else if (index === selectedOption && selectedOption !== data.correctAnswer) {
                    opt.classList.add('incorrect');
                }
            });

            // Show feedback message
            if (data.correct) {
                resultMessage.textContent = 'Correct! Well done.';
                feedbackContainer.className = 'correct';
            } else {
                resultMessage.textContent = 'Incorrect. The correct answer is shown.';
                feedbackContainer.className = 'incorrect';
            }

            explanation.textContent = data.explanation;

            // Add source URL
            if (data.sourceUrl) {
                sourceLink.href = data.sourceUrl;
                sourceLink.parentElement.style.display = 'block';
            } else {
                sourceLink.parentElement.style.display = 'none';
            }

            feedbackContainer.classList.remove('hidden');

            // Handle final question
            if (!data.nextQuestion) {
                nextButton.textContent = 'See Results';
            }
        })
        .catch(error => {
            console.error('Error submitting answer:', error);
            alert('Error submitting your answer. Please try again.');
        });
    }
});