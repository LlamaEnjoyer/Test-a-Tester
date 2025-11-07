/**
 * Question page timer functionality
 * Handles countdown timer display and auto-submission when time expires
 * Implements clock skew detection to prevent client-side timer manipulation
 */

// Constants
const SECONDS_PER_MINUTE = 60;
const TIMER_DANGER_THRESHOLD = 60;  // Red warning when <= 60 seconds
const TIMER_WARNING_THRESHOLD = 180;  // Yellow warning when <= 180 seconds
const CLOCK_SKEW_LOG_THRESHOLD = 2;  // Log warning if skew > 2 seconds
const TIME_DISPLAY_PADDING = 2;  // Padding for seconds display (padStart)

try {
    // Get timer element and data attributes
    const timerElement = document.getElementById('timer');
    const timeDisplay = document.getElementById('time-display');

    if (!timerElement || !timeDisplay) {
        throw new Error('Required timer elements not found');
    }

    // Initialize remaining time from server (in seconds)
    let remainingTime = parseInt(timerElement.dataset.remainingTime, 10);

    if (isNaN(remainingTime) || remainingTime < 0) {
        throw new Error('Invalid remaining time value');
    }

    // Get server timestamp for clock skew detection
    const serverTimestamp = parseFloat(timerElement.dataset.serverTimestamp);
    const clientTimestamp = Date.now() / 1000; // Convert to seconds

    if (isNaN(serverTimestamp)) {
        throw new Error('Invalid server timestamp');
    }

    // Calculate clock skew (difference between server and client time)
    const clockSkew = serverTimestamp - clientTimestamp;

    // Log significant clock skew for debugging
    if (Math.abs(clockSkew) > CLOCK_SKEW_LOG_THRESHOLD) {
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
        try {
            const minutes = Math.floor(seconds / SECONDS_PER_MINUTE);
            const secs = seconds % SECONDS_PER_MINUTE;
            return `${minutes}:${secs.toString().padStart(TIME_DISPLAY_PADDING, '0')}`;
        } catch (error) {
            console.error('Error formatting time:', error);
            return '0:00';
        }
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
        try {
            // Calculate remaining time based on server-synced clock
            const currentTime = getServerSyncedTime();
            const elapsedTime = currentTime - timerStartTime;
            const calculatedRemainingTime = Math.max(0, remainingTime - Math.floor(elapsedTime));

            if (calculatedRemainingTime <= 0) {
                // Time's up - redirect to score page
                const scoreUrl = timerElement.dataset.scoreUrl;
                if (scoreUrl) {
                    window.location.href = scoreUrl;
                } else {
                    console.error('Score URL not found');
                }
                return;
            }

            timeDisplay.textContent = formatTime(calculatedRemainingTime);

            // Update timer styling based on remaining time
            if (calculatedRemainingTime <= TIMER_DANGER_THRESHOLD) {
                timerElement.className = 'timer danger';
            } else if (calculatedRemainingTime <= TIMER_WARNING_THRESHOLD) {
                timerElement.className = 'timer warning';
            } else {
                timerElement.className = 'timer';
            }
        } catch (error) {
            console.error('Error updating timer:', error);
            clearInterval(timerInterval);
        }
    }

    // Update timer immediately, then every second
    updateTimer();
    const timerInterval = setInterval(updateTimer, 1000);

    // Add client timestamp to form submission for server-side validation
    const quizForm = document.getElementById('quiz-form');
    if (quizForm) {
        quizForm.addEventListener('submit', function () {
            try {
                // Set current client timestamp (server-synced) when submitting
                const clientTimestampField = document.getElementById('client_timestamp');
                if (clientTimestampField) {
                    clientTimestampField.value = getServerSyncedTime().toFixed(3);
                }
                clearInterval(timerInterval);
            } catch (error) {
                console.error('Error on form submit:', error);
                // Still allow form submission even if timestamp update fails
            }
        });
    }

} catch (error) {
    console.error('Critical error initializing timer:', error);
    // Display error message to user
    const timeDisplay = document.getElementById('time-display');
    if (timeDisplay) {
        timeDisplay.textContent = 'Error';
    }
}
