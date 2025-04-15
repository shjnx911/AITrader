/**
 * Theme management for AITradeStrategist
 * Supports light and dark modes with system preference detection
 */

// Theme constants
const THEME_STORAGE_KEY = 'aitrader_theme';
const THEME_DARK = 'dark';
const THEME_LIGHT = 'light';
const THEME_AUTO = 'auto';

// Function to get current system theme preference
function getSystemThemePreference() {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches 
        ? THEME_DARK 
        : THEME_LIGHT;
}

// Function to get saved theme preference
function getSavedTheme() {
    return localStorage.getItem(THEME_STORAGE_KEY) || THEME_AUTO;
}

// Function to save theme preference
function saveThemePreference(theme) {
    localStorage.setItem(THEME_STORAGE_KEY, theme);
}

// Function to apply theme
function applyTheme(theme) {
    // If theme is auto, determine based on system preference
    const effectiveTheme = theme === THEME_AUTO 
        ? getSystemThemePreference() 
        : theme;
    
    // Apply theme to document
    document.documentElement.setAttribute('data-bs-theme', effectiveTheme);
    
    // Update active state in UI
    updateThemeUI(theme);
    
    // Dispatch custom event for theme change
    document.dispatchEvent(new CustomEvent('themeChanged', { 
        detail: { theme: effectiveTheme, preference: theme } 
    }));
}

// Function to update UI components based on current theme
function updateThemeUI(theme) {
    // Find theme toggle elements
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const lightModeToggle = document.getElementById('light-mode-toggle');
    const systemModeToggle = document.getElementById('system-mode-toggle');
    const themeToggleIcon = document.getElementById('theme-toggle-icon');
    
    // Update toggle states if they exist
    if (darkModeToggle) {
        darkModeToggle.checked = theme === THEME_DARK;
    }
    
    if (lightModeToggle) {
        lightModeToggle.checked = theme === THEME_LIGHT;
    }
    
    if (systemModeToggle) {
        systemModeToggle.checked = theme === THEME_AUTO;
    }
    
    // Update icon if exists
    if (themeToggleIcon) {
        const currentTheme = theme === THEME_AUTO 
            ? getSystemThemePreference() 
            : theme;
            
        if (currentTheme === THEME_DARK) {
            themeToggleIcon.classList.remove('bi-sun');
            themeToggleIcon.classList.add('bi-moon');
        } else {
            themeToggleIcon.classList.remove('bi-moon');
            themeToggleIcon.classList.add('bi-sun');
        }
    }
}

// Function to set theme
function setTheme(theme) {
    if (![THEME_LIGHT, THEME_DARK, THEME_AUTO].includes(theme)) {
        console.error('Invalid theme:', theme);
        return;
    }
    
    saveThemePreference(theme);
    applyTheme(theme);
}

// Function to toggle between light and dark themes
function toggleTheme() {
    const currentTheme = getSavedTheme();
    
    // If current theme is auto, determine the current effective theme and toggle from there
    if (currentTheme === THEME_AUTO) {
        const currentEffectiveTheme = getSystemThemePreference();
        setTheme(currentEffectiveTheme === THEME_DARK ? THEME_LIGHT : THEME_DARK);
    } else {
        // Otherwise just toggle between dark and light
        setTheme(currentTheme === THEME_DARK ? THEME_LIGHT : THEME_DARK);
    }
}

// Initialize theme system
function initTheme() {
    // Apply the saved theme or system default
    const savedTheme = getSavedTheme();
    applyTheme(savedTheme);
    
    // Set up event listeners for theme toggles
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', toggleTheme);
    }
    
    // Set up radio group event listeners if they exist
    const themeRadios = document.querySelectorAll('input[name="theme-option"]');
    themeRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (e.target.checked) {
                setTheme(e.target.value);
            }
        });
    });
    
    // Listen for system theme preference changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    mediaQuery.addEventListener('change', () => {
        // If the theme is set to auto, update based on new system preference
        if (getSavedTheme() === THEME_AUTO) {
            applyTheme(THEME_AUTO);
        }
    });
}

// Initialize when the DOM is ready
document.addEventListener('DOMContentLoaded', initTheme);

// Export functions for use in other scripts
window.themeManager = {
    getTheme: getSavedTheme,
    setTheme,
    toggleTheme,
    isSystemDarkMode: () => getSystemThemePreference() === THEME_DARK
};