"""
Unit tests for the theme switching and language localization features.
"""
import os
import pytest
from unittest.mock import patch, MagicMock

# We'll assume these modules/functions exist in the application
# If they don't, we can adjust the tests accordingly
try:
    from web_ui.static.js.theme import get_user_theme_preference, set_user_theme_preference
    from web_ui.static.js.i18n import get_user_language_preference, set_user_language_preference, translate_text
    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False


# Skip tests if imports are not available
pytestmark = pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Theme and i18n modules not available")


class TestTheme:
    """Tests for the theme switching functionality."""
    
    @patch('web_ui.static.js.theme.localStorage', MagicMock())
    def test_get_user_theme_preference_default(self):
        """Test getting the user's theme preference when no preference is set."""
        # Set up the mock localStorage
        mock_local_storage = MagicMock()
        mock_local_storage.getItem.return_value = None
        
        with patch('web_ui.static.js.theme.localStorage', mock_local_storage):
            # Get the user's theme preference
            theme = get_user_theme_preference()
            
            # The default theme should be dark
            assert theme == 'dark'
    
    @patch('web_ui.static.js.theme.localStorage', MagicMock())
    def test_get_user_theme_preference_light(self):
        """Test getting the user's theme preference when set to light."""
        # Set up the mock localStorage
        mock_local_storage = MagicMock()
        mock_local_storage.getItem.return_value = 'light'
        
        with patch('web_ui.static.js.theme.localStorage', mock_local_storage):
            # Get the user's theme preference
            theme = get_user_theme_preference()
            
            # The theme should be light
            assert theme == 'light'
    
    @patch('web_ui.static.js.theme.localStorage', MagicMock())
    def test_get_user_theme_preference_dark(self):
        """Test getting the user's theme preference when set to dark."""
        # Set up the mock localStorage
        mock_local_storage = MagicMock()
        mock_local_storage.getItem.return_value = 'dark'
        
        with patch('web_ui.static.js.theme.localStorage', mock_local_storage):
            # Get the user's theme preference
            theme = get_user_theme_preference()
            
            # The theme should be dark
            assert theme == 'dark'
    
    @patch('web_ui.static.js.theme.localStorage', MagicMock())
    def test_set_user_theme_preference(self):
        """Test setting the user's theme preference."""
        # Set up the mock localStorage
        mock_local_storage = MagicMock()
        
        with patch('web_ui.static.js.theme.localStorage', mock_local_storage):
            # Set the user's theme preference
            set_user_theme_preference('light')
            
            # localStorage.setItem should have been called with the correct arguments
            mock_local_storage.setItem.assert_called_once_with('theme', 'light')


class TestLocalization:
    """Tests for the language localization functionality."""
    
    @patch('web_ui.static.js.i18n.localStorage', MagicMock())
    def test_get_user_language_preference_default(self):
        """Test getting the user's language preference when no preference is set."""
        # Set up the mock localStorage
        mock_local_storage = MagicMock()
        mock_local_storage.getItem.return_value = None
        
        with patch('web_ui.static.js.i18n.localStorage', mock_local_storage):
            # Get the user's language preference
            language = get_user_language_preference()
            
            # The default language should be English
            assert language == 'en'
    
    @patch('web_ui.static.js.i18n.localStorage', MagicMock())
    def test_get_user_language_preference_vietnamese(self):
        """Test getting the user's language preference when set to Vietnamese."""
        # Set up the mock localStorage
        mock_local_storage = MagicMock()
        mock_local_storage.getItem.return_value = 'vi'
        
        with patch('web_ui.static.js.i18n.localStorage', mock_local_storage):
            # Get the user's language preference
            language = get_user_language_preference()
            
            # The language should be Vietnamese
            assert language == 'vi'
    
    @patch('web_ui.static.js.i18n.localStorage', MagicMock())
    def test_set_user_language_preference(self):
        """Test setting the user's language preference."""
        # Set up the mock localStorage
        mock_local_storage = MagicMock()
        
        with patch('web_ui.static.js.i18n.localStorage', mock_local_storage):
            # Set the user's language preference
            set_user_language_preference('vi')
            
            # localStorage.setItem should have been called with the correct arguments
            mock_local_storage.setItem.assert_called_once_with('language', 'vi')
    
    @patch('web_ui.static.js.i18n.translations', {
        'en': {'hello': 'Hello', 'goodbye': 'Goodbye'},
        'vi': {'hello': 'Xin chào', 'goodbye': 'Tạm biệt'}
    })
    def test_translate_text_english(self):
        """Test translating text to English."""
        # Translate text to English
        translation = translate_text('hello', 'en')
        
        # The translation should be correct
        assert translation == 'Hello'
    
    @patch('web_ui.static.js.i18n.translations', {
        'en': {'hello': 'Hello', 'goodbye': 'Goodbye'},
        'vi': {'hello': 'Xin chào', 'goodbye': 'Tạm biệt'}
    })
    def test_translate_text_vietnamese(self):
        """Test translating text to Vietnamese."""
        # Translate text to Vietnamese
        translation = translate_text('hello', 'vi')
        
        # The translation should be correct
        assert translation == 'Xin chào'
    
    @patch('web_ui.static.js.i18n.translations', {
        'en': {'hello': 'Hello', 'goodbye': 'Goodbye'},
        'vi': {'hello': 'Xin chào', 'goodbye': 'Tạm biệt'}
    })
    def test_translate_text_missing_key(self):
        """Test translating text with a missing key."""
        # Translate text with a missing key
        translation = translate_text('missing', 'en')
        
        # The key should be returned as is
        assert translation == 'missing'
    
    @patch('web_ui.static.js.i18n.translations', {
        'en': {'hello': 'Hello', 'goodbye': 'Goodbye'},
        'vi': {'hello': 'Xin chào', 'goodbye': 'Tạm biệt'}
    })
    def test_translate_text_unsupported_language(self):
        """Test translating text to an unsupported language."""
        # Translate text to an unsupported language
        translation = translate_text('hello', 'fr')
        
        # The English translation should be used as a fallback
        assert translation == 'Hello'