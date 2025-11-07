/**
 * Question page timer functionality
 * Handles countdown timer display and auto-submission when time expires
 * Implements clock skew detection to prevent client-side timer manipulation
 */

// Get timer element and data attributes
const timerElement = document.getElementById('timer');
const timeDisplay = document.getElementById('time-display');

// Initialize remaining time from server (in seconds)
let remainingTime = parseInt(timerElement.dataset.remainingTime, 10);

// Get server timestamp for clock skew detection
const serverTimestamp = parseFloat(timerElement.dataset.serverTimestamp);
const clientTimestamp = Date.now() / 1000; // Convert to seconds

// Calculate clock skew (difference between server and client time)
const clockSkew = serverTimestamp - clientTimestamp;

// Log significant clock skew for debugging
if (Math.abs(clockSkew) > 2) {
    console.warn(`Clock skew detected: ${clockSkew.toFixed(2)} seconds`);
    console.warn('Timer will sync with server time to prevent drift');
}

// Store the corrected start time (server time when page loaded)
const timerStartTime = Date.now() / 1000 + clockSkew;

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
 * Get current time adjusted for clock skew
 * @returns {number} Current time in seconds, synchronized with server
 */
function getServerSyncedTime() {
    return Date.now() / 1000 + clockSkew;
}

/**
 * Update the timer display and handle expiration
 */
function updateTimer() {
    // Calculate remaining time based on server-synced clock
    const currentTime = getServerSyncedTime();
    const elapsedTime = currentTime - timerStartTime;
    const calculatedRemainingTime = Math.max(0, remainingTime - Math.floor(elapsedTime));

    if (calculatedRemainingTime <= 0) {
        // Time's up - redirect to score page
        window.location.href = timerElement.dataset.scoreUrl;
        return;
    }

    timeDisplay.textContent = formatTime(calculatedRemainingTime);

    // Update timer styling based on remaining time
    if (calculatedRemainingTime <= 60) {
        timerElement.className = 'timer danger';
    } else if (calculatedRemainingTime <= 180) {
        timerElement.className = 'timer warning';
    } else {
        timerElement.className = 'timer';
    }
}

// Update timer immediately, then every second
updateTimer();
const timerInterval = setInterval(updateTimer, 1000);

// Add client timestamp to form submission for server-side validation
document.getElementById('quiz-form').addEventListener('submit', function () {
    // Set current client timestamp (server-synced) when submitting
    const clientTimestampField = document.getElementById('client_timestamp');
    if (clientTimestampField) {
        clientTimestampField.value = getServerSyncedTime().toFixed(3);
    }
    clearInterval(timerInterval);
});
