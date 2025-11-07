/**
 * Start page form validation and dynamic question limit calculation
 * Handles category selection validation and max question updates
 */

try {
    // Category counts for each category (parsed from data attribute)
    const categoryDataElement = document.getElementById('category-data');
    if (!categoryDataElement) {
        throw new Error('Category data element not found');
    }

    const categoryCounts = JSON.parse(categoryDataElement.dataset.categoryCounts);
    const numQuestionsInput = document.getElementById('num_questions');
    const rangeText = document.querySelector('.range-text');

    if (!numQuestionsInput || !rangeText) {
        throw new Error('Required form elements not found');
    }

    /**
     * Update the maximum number of questions based on selected categories
     */
    function updateMaxQuestions() {
        try {
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
        } catch (error) {
            console.error('Error updating max questions:', error);
        }
    }

    // Form submission validation
    const configForm = document.querySelector('.config-form');
    if (configForm) {
        configForm.addEventListener('submit', function (e) {
            try {
                const checkboxes = document.querySelectorAll('input[name="categories"]:checked');
                const errorMessage = document.getElementById('category-error');

                if (!errorMessage) {
                    console.warn('Category error message element not found');
                    return;
                }

                if (checkboxes.length === 0) {
                    e.preventDefault();
                    errorMessage.style.display = 'block';
                    return false;
                } else {
                    errorMessage.style.display = 'none';
                }
            } catch (error) {
                console.error('Error in form submission handler:', error);
            }
        });
    }

    // Hide error message and update max questions when user checks a category
    document.querySelectorAll('input[name="categories"]').forEach(function (checkbox) {
        checkbox.addEventListener('change', function () {
            try {
                const anyChecked = document.querySelectorAll('input[name="categories"]:checked').length > 0;
                const errorMessage = document.getElementById('category-error');

                if (errorMessage && anyChecked) {
                    errorMessage.style.display = 'none';
                }
                updateMaxQuestions();
            } catch (error) {
                console.error('Error in checkbox change handler:', error);
            }
        });
    });

} catch (error) {
    console.error('Critical error initializing start page:', error);
}
