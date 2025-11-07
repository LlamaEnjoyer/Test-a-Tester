/**
 * Start page form validation and dynamic question limit calculation
 * Handles category selection validation and max question updates
 */

// Category counts for each category (parsed from data attribute)
const categoryCounts = JSON.parse(document.getElementById('category-data').dataset.categoryCounts);
const numQuestionsInput = document.getElementById('num_questions');
const rangeText = document.querySelector('.range-text');

/**
 * Update the maximum number of questions based on selected categories
 */
function updateMaxQuestions() {
    const selectedCategories = Array.from(document.querySelectorAll('input[name="categories"]:checked'))
        .map(cb => cb.value);

    let maxQuestions = 0;
    selectedCategories.forEach(cat => {
        maxQuestions += categoryCounts[cat] || 0;
    });

    if (maxQuestions > 0) {
        numQuestionsInput.max = maxQuestions;
        if (parseInt(numQuestionsInput.value) > maxQuestions) {
            numQuestionsInput.value = maxQuestions;
        }
        rangeText.textContent = `(1 - ${maxQuestions})`;
    }
}

// Form submission validation
document.querySelector('.config-form').addEventListener('submit', function (e) {
    const checkboxes = document.querySelectorAll('input[name="categories"]:checked');
    const errorMessage = document.getElementById('category-error');

    if (checkboxes.length === 0) {
        e.preventDefault();
        errorMessage.style.display = 'block';
        return false;
    } else {
        errorMessage.style.display = 'none';
    }
});

// Hide error message and update max questions when user checks a category
document.querySelectorAll('input[name="categories"]').forEach(function (checkbox) {
    checkbox.addEventListener('change', function () {
        const anyChecked = document.querySelectorAll('input[name="categories"]:checked').length > 0;
        if (anyChecked) {
            document.getElementById('category-error').style.display = 'none';
        }
        updateMaxQuestions();
    });
});
