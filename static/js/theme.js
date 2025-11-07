// Shared theme toggle logic
// Enhancements:
// 1. Adds a temporary 'no-theme-transition' class to suppress transitions on first paint.
// 2. Applies prefers-color-scheme when no saved theme exists.
// 3. Defers initialization until DOMContentLoaded if script is moved to <head>.
(function () {
    function applyInitialTheme() {
        try {
            const body = document.body;
            if (!body) return;

            // Determine theme: saved -> prefers-color-scheme -> default light
            const saved = localStorage.getItem('theme');
            let effective = saved;
            if (!effective) {
                try {
                    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
                    effective = prefersDark ? 'dark' : 'light';
                } catch (e) {
                    console.warn('Error detecting color scheme preference:', e);
                    effective = 'light';
                }
            }

            if (effective === 'dark') {
                body.classList.add('dark-mode');
            }

            // Remove the no-transition class on next frame so subsequent toggles animate
            requestAnimationFrame(() => {
                body.classList.remove('no-theme-transition');
            });

            return effective;
        } catch (error) {
            console.error('Error applying initial theme:', error);
            return 'light';
        }
    }

    function initThemeToggle() {
        try {
            const themeToggle = document.getElementById('theme-toggle');
            const themeIcon = document.getElementById('theme-icon');
            const body = document.body;

            if (!body || !themeToggle || !themeIcon) {
                console.warn('Theme toggle elements not found');
                return;
            }

            const currentApplied = body.classList.contains('dark-mode') ? 'dark' : 'light';
            themeIcon.textContent = currentApplied === 'dark' ? '☀️' : '🌙';

            themeToggle.addEventListener('click', () => {
                try {
                    const isDark = body.classList.toggle('dark-mode');
                    if (isDark) {
                        themeIcon.textContent = '☀️';
                        localStorage.setItem('theme', 'dark');
                    } else {
                        themeIcon.textContent = '🌙';
                        localStorage.setItem('theme', 'light');
                    }
                } catch (error) {
                    console.error('Error toggling theme:', error);
                }
            });
        } catch (error) {
            console.error('Error initializing theme toggle:', error);
        }
    }

    function bootstrap() {
        try {
            applyInitialTheme();
            initThemeToggle();
        } catch (error) {
            console.error('Error bootstrapping theme:', error);
        }
    }

    if (document.readyState === 'loading') {
        // If placed in <head>, wait for body elements.
        document.addEventListener('DOMContentLoaded', bootstrap);
    } else {
        bootstrap();
    }
})();
