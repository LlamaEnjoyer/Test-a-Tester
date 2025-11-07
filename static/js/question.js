/**
 * Question page timer functionality
 * Handles countdown timer display and auto-submission when time expires
 */

// Initialize remaining time from server (in seconds)
let remainingTime = parseInt(document.getElementById('timer').dataset.remainingTime, 10);
const timerElement = document.getElementById('timer');
const timeDisplay = document.getElementById('time-display');

/**
 * Format seconds into MM:SS format
 * @param {number} seconds - Time in seconds
 * @returns {string} Formatted time string
 */
function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

/**
 * Update the timer display and handle expiration
 */
function updateTimer() {
    if (remainingTime <= 0) {
        // Time's up - redirect to score page
        window.location.href = timerElement.dataset.scoreUrl;
        return;
    }

    timeDisplay.textContent = formatTime(remainingTime);

    // Update timer styling based on remaining time
    if (remainingTime <= 60) {
        timerElement.className = 'timer danger';
    } else if (remainingTime <= 180) {
        timerElement.className = 'timer warning';
    } else {
        timerElement.className = 'timer';
    }

    remainingTime--;
}

// Update timer immediately, then every second
updateTimer();
const timerInterval = setInterval(updateTimer, 1000);

// Clear interval when form is submitted
document.getElementById('quiz-form').addEventListener('submit', function () {
    clearInterval(timerInterval);
});
