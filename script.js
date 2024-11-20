document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search');
    const beginnerCheckbox = document.getElementById('beginner');
    const intermediateCheckbox = document.getElementById('intermediate');
    const advancedCheckbox = document.getElementById('advanced');
    const lessonList = document.getElementById('lesson-list');

    searchInput.addEventListener('input', filterLessons);
    beginnerCheckbox.addEventListener('change', filterLessons);
    intermediateCheckbox.addEventListener('change', filterLessons);
    advancedCheckbox.addEventListener('change', filterLessons);

    function filterLessons() {
        const searchValue = searchInput.value.toLowerCase();
        const beginnerChecked = beginnerCheckbox.checked;
        const intermediateChecked = intermediateCheckbox.checked;
        const advancedChecked = advancedCheckbox.checked;

        Array.from(lessonList.children).forEach(lesson => {
            const title = lesson.querySelector('h3').textContent.toLowerCase();
            const difficulty = lesson.querySelector('p:nth-child(3)').textContent.split(': ')[1];

            const matchesSearch = title.includes(searchValue);
            const matchesDifficulty = (beginnerChecked && difficulty === 'Beginner') ||
                                    (intermediateChecked && difficulty === 'Intermediate') ||
                                    (advancedChecked && difficulty === 'Advanced') ||
                                    (!beginnerChecked && !intermediateChecked && !advancedChecked);

            lesson.style.display = matchesSearch && matchesDifficulty ? '' : 'none';
        });
    }

    document.querySelectorAll('.start-lesson').forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault();
            const lessonId = button.getAttribute('data-id');
            alert(`Starting lesson with ID: ${lessonId}`);
            // Add logic to navigate to the lesson detail page
        });
    });
});

function sendMessage() {
    const userInput = document.getElementById('userInput').value;
    if (userInput.trim() === '') return;

    appendMessage('user', userInput);

    // Simulate a response from the chatbot
    setTimeout(() => {
        const response = getBotResponse(userInput);
        appendMessage('bot', response);
    }, 1000);

    document.getElementById('userInput').value = '';
}

function appendMessage(sender, message) {
    const messagesContainer = document.getElementById('messages');
    const messageElement = document.createElement('div');
    messageElement.className = sender;
    messageElement.textContent = message;
    messagesContainer.appendChild(messageElement);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function getBotResponse(input) {
    const lowerCaseInput = input.toLowerCase();
    if (lowerCaseInput.includes('hello')) {
        return 'Hello! How can I assist you today?';
    } else if (lowerCaseInput.includes('help')) {
        return 'Sure, what do you need help with?';
    } else if (lowerCaseInput.includes('bye')) {
        return 'Goodbye! Have a great day!';
    } else {
        return "I'm not sure how to respond to that. Can you please rephrase?";
    }
}