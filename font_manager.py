#!/usr/bin/env python
"""
Font Manager - Class for managing fonts for CV templates.
"""
import os
import logging
import sys
from typing import Dict, Any, Optional

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Configure logging
logger = logging.getLogger('font_manager')

class FontManager:
    """
    Manages font registration and ensures required fonts are available.
    """

    def __init__(self, debug_mode=False):
        """Initialize with default font configuration."""
        self.fonts_registered = set()
        self.debug_mode = debug_mode
        
        if self.debug_mode:
            logger.setLevel(logging.DEBUG)
            
        # Register standard PDF fonts
        self._register_standard_fonts()
        
        self.default_fonts_config = {
            "font_awesome": {
                "name": "FontAwesome",
                "path": "fonts/fontawesome-webfont.ttf",
                "url": "https://unpkg.com/font-awesome@4.7.0/fonts/fontawesome-webfont.ttf"
            },
            "DejaVuSans": {
                "name": "DejaVuSans",
                "path": "fonts/DejaVuSans.ttf"
            },
            "DejaVuSans-Bold": {
                "name": "DejaVuSans-Bold",
                "path": "fonts/DejaVuSans-Bold.ttf"
            }
        }
        
        # Always register standard fonts as fallbacks
        self.fallback_map = {
            "DejaVuSans": "Helvetica",
            "DejaVuSans-Bold": "Helvetica-Bold",
            "FontAwesome": "Helvetica"
        }

    def _register_standard_fonts(self):
        """Register the standard 14 PDF fonts."""
        # These are built into ReportLab/PDF and don't need TTF files
        self.fonts_registered.add("Helvetica")
        self.fonts_registered.add("Helvetica-Bold")
        self.fonts_registered.add("Helvetica-Oblique")
        self.fonts_registered.add("Helvetica-BoldOblique")
        self.fonts_registered.add("Courier")
        self.fonts_registered.add("Courier-Bold")
        self.fonts_registered.add("Courier-Oblique")
        self.fonts_registered.add("Courier-BoldOblique")
        self.fonts_registered.add("Times-Roman")
        self.fonts_registered.add("Times-Bold")
        self.fonts_registered.add("Times-Italic")
        self.fonts_registered.add("Times-BoldItalic")
        self.fonts_registered.add("Symbol")
        self.fonts_registered.add("ZapfDingbats")
        logger.debug("Registered standard 14 PDF fonts")

    def register_font(self, font_name: str, font_path: str) -> bool:
        """
        Register a font with ReportLab.

        Args:
            font_name: Name to register the font as
            font_path: Path to the TTF file

        Returns:
            True if registration successful, False otherwise
        """
        try:
            if font_name in self.fonts_registered:
                logger.debug(f"Font '{font_name}' already registered")
                return True

            if not os.path.exists(font_path):
                logger.warning(f"Font file not found: {font_path}")
                # Use fallback font if available
                if font_name in self.fallback_map:
                    fallback = self.fallback_map[font_name]
                    logger.warning(f"Using '{fallback}' as fallback for '{font_name}'")
                    
                    # Explicitly create font alias - more reliable than addMapping
                    pdfmetrics.registerFontFamily(
                        font_name,
                        normal=fallback,
                        bold=fallback.replace('Helvetica', 'Helvetica-Bold') if fallback == 'Helvetica' else fallback,
                        italic=fallback.replace('Helvetica', 'Helvetica-Oblique') if fallback == 'Helvetica' else fallback,
                        boldItalic=fallback.replace('Helvetica', 'Helvetica-BoldOblique') if fallback == 'Helvetica' else fallback
                    )
                    self.fonts_registered.add(font_name)
                    logger.debug(f"Created font alias: {font_name} -> {fallback}")
                    return True
                return False

            # Try registering the font
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                self.fonts_registered.add(font_name)
                logger.debug(f"Successfully registered font: {font_name}")
                
                # Register DejaVu font family if this is a DejaVu font
                if font_name == "DejaVuSans" or font_name == "DejaVuSans-Bold":
                    # Check if both regular and bold are available before registering family
                    has_dejavu_regular = "DejaVuSans" in self.fonts_registered or os.path.exists("fonts/DejaVuSans.ttf")
                    has_dejavu_bold = "DejaVuSans-Bold" in self.fonts_registered or os.path.exists("fonts/DejaVuSans-Bold.ttf")
                    
                    # If both aren't available yet, register what we have individually
                    if not (has_dejavu_regular and has_dejavu_bold):
                        logger.debug(f"Registered {font_name} individually, waiting for other DejaVu fonts before family registration")
                        return True
                        
                    # Register the complete DejaVu family
                    logger.debug("Registering complete DejaVuSans font family")
                    pdfmetrics.registerFontFamily(
                        'DejaVuSans',
                        normal='DejaVuSans',
                        bold='DejaVuSans-Bold',
                        italic='DejaVuSans',  # No italic version, use normal
                        boldItalic='DejaVuSans-Bold'  # No bold-italic, use bold
                    )
                
                return True
            except Exception as e:
                logger.error(f"Error registering font {font_name}: {e}")
                # Use fallback font if available
                if font_name in self.fallback_map:
                    fallback = self.fallback_map[font_name]
                    logger.warning(f"Using '{fallback}' as fallback for '{font_name}'")
                    
                    # Explicitly create font alias - more reliable than addMapping
                    pdfmetrics.registerFontFamily(
                        font_name,
                        normal=fallback,
                        bold=fallback.replace('Helvetica', 'Helvetica-Bold') if fallback == 'Helvetica' else fallback,
                        italic=fallback.replace('Helvetica', 'Helvetica-Oblique') if fallback == 'Helvetica' else fallback,
                        boldItalic=fallback.replace('Helvetica', 'Helvetica-BoldOblique') if fallback == 'Helvetica' else fallback
                    )
                    self.fonts_registered.add(font_name)
                    logger.debug(f"Created font alias: {font_name} -> {fallback}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Unexpected error registering font {font_name}: {e}")
            return False

    def ensure_fonts_available(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Ensure all required fonts are available and registered.
        Attempts to download them if not found locally.

        Args:
            config: Optional font configuration to override defaults
        """
        logger.debug("Ensuring required fonts are available")
        
        # Create fonts directory if it doesn't exist
        os.makedirs("fonts", exist_ok=True)
        
        merged_config = self.default_fonts_config.copy()
        if config:
            merged_config.update(config)

        # Load icon font (Font Awesome) first
        fa_config = merged_config.pop("font_awesome", None)
        if fa_config:
            self.load_font_with_download(fa_config)

        # Register any additional fonts, attempting download if necessary
        for font_name, font_config_entry in merged_config.items():
            if isinstance(font_config_entry, dict):
                self.load_font_with_download(font_config_entry)
        
        # Specifically handle the DejaVu font family registration
        dejavu_regular = "DejaVuSans" in self.fonts_registered
        dejavu_bold = "DejaVuSans-Bold" in self.fonts_registered
        
        if dejavu_regular and dejavu_bold:
            logger.debug("Both DejaVuSans and DejaVuSans-Bold are registered, ensuring font family is set up")
            try:
                # Register the complete DejaVu family explicitly
                pdfmetrics.registerFontFamily(
                    'DejaVuSans',
                    normal='DejaVuSans',
                    bold='DejaVuSans-Bold',
                    italic='DejaVuSans',  # No italic version, use normal
                    boldItalic='DejaVuSans-Bold'  # No bold-italic, use bold
                )
                logger.debug("DejaVuSans font family registered successfully")
            except Exception as e:
                logger.error(f"Error registering DejaVuSans font family: {e}")
                
        # Make 100% sure that standard PDF fonts are available as fallbacks
        self._ensure_standard_fonts_available()
                
        logger.debug(f"Registered fonts: {self.fonts_registered}")
        
        # If DejaVu fonts are still not registered, try to load them directly
        if "DejaVuSans" not in self.fonts_registered or "DejaVuSans-Bold" not in self.fonts_registered:
            logger.warning("DejaVu fonts not fully registered, attempting direct registration")
            self._register_dejavu_fonts_directly()

    def _ensure_standard_fonts_available(self):
        """Ensure that standard PDF fonts are always available as fallbacks."""
        # Force register/map DejaVu fonts to standard fonts if they weren't successfully registered
        if "DejaVuSans" not in self.fonts_registered or "DejaVuSans-Bold" not in self.fonts_registered:
            logger.warning("DejaVu fonts not available, explicitly creating fallbacks")
            
            # Register DejaVu base font name as alias for Helvetica
            pdfmetrics.registerFontFamily(
                'DejaVuSans',
                normal='Helvetica',
                bold='Helvetica-Bold',
                italic='Helvetica-Oblique',
                boldItalic='Helvetica-BoldOblique'
            )
            
            self.fonts_registered.add("DejaVuSans")
            self.fonts_registered.add("DejaVuSans-Bold")
        
        # Force FontAwesome as Helvetica if needed
        if "FontAwesome" not in self.fonts_registered:
            logger.warning("FontAwesome not available, using Helvetica as fallback")
            # Just register normal Helvetica as fallback for icons
            pdfmetrics.registerFontFamily(
                'FontAwesome',
                normal='Helvetica',
                bold='Helvetica-Bold',
                italic='Helvetica-Oblique',
                boldItalic='Helvetica-BoldOblique'
            )
            self.fonts_registered.add("FontAwesome")

    def load_font_with_download(self, font_config: Dict[str, Any]) -> bool:
        """
        Loads a single font, attempting to download it if not found locally.

        Args:
            font_config: Dictionary with font "name", "path", and optional "url".

        Returns:
            True if loading successful, False otherwise.
        """
        font_name = font_config.get("name")
        font_path = font_config.get("path")
        font_url = font_config.get("url")

        if not font_name or not font_path:
            logger.warning(f"Skipping font due to missing name or path in config: {font_config}")
            return False

        # Check if already registered
        if font_name in self.fonts_registered:
            logger.debug(f"Font '{font_name}' already registered")
            return True

        # If font file doesn't exist and URL is provided, try to download it
        if not os.path.exists(font_path) and font_url:
            logger.info(f"Font {font_name} not found at {font_path}. Attempting download from {font_url}")
            try:
                self._download_font(font_url, font_path)
            except Exception as e:
                logger.error(f"Error downloading font {font_name}: {e}")
                # If download fails, we'll try to use a fallback font
                if font_name in self.fallback_map:
                    logger.warning(f"Using '{self.fallback_map[font_name]}' as fallback for '{font_name}'")
                    # Map font name to fallback in reportlab's font mapping
                    pdfmetrics.addMapping(font_name, 0, 0, self.fallback_map[font_name])
                    self.fonts_registered.add(font_name)
                    return True
                return False

        # Register the font
        return self.register_font(font_name, font_path)

    def _download_font(self, url: str, path: str) -> None:
        """
        Download a font from a URL.

        Args:
            url: URL to download from
            path: Path to save to

        Raises:
            Exception: If download fails
        """
        try:
            import requests
        except ImportError:
            logger.error("Python requests module not installed. Cannot download fonts.")
            logger.error("Install it with: pip install requests")
            raise Exception("Python requests module not installed")

        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

        logger.info(f"Downloading font from: {url}")
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                with open(path, "wb") as f:
                    f.write(response.content)
                logger.info(f"Downloaded {path} successfully")
            else:
                raise Exception(f"Failed to download from {url} (status code: {response.status_code})")
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error downloading font: {e}")
            raise
        except Exception as e:
            logger.error(f"Error saving downloaded font: {e}")
            raise

    def _register_dejavu_fonts_directly(self):
        """
        Registers DejaVuSans and DejaVuSans-Bold directly if they are not registered.
        """
        dejavu_normal_registered = False
        dejavu_bold_registered = False
        
        if "DejaVuSans" not in self.fonts_registered:
            logger.warning("DejaVuSans not registered, attempting direct registration")
            dejavu_normal_registered = self.register_font("DejaVuSans", "fonts/DejaVuSans.ttf")
        else:
            dejavu_normal_registered = True

        if "DejaVuSans-Bold" not in self.fonts_registered:
            logger.warning("DejaVuSans-Bold not registered, attempting direct registration")
            dejavu_bold_registered = self.register_font("DejaVuSans-Bold", "fonts/DejaVuSans-Bold.ttf")
        else:
            dejavu_bold_registered = True
            
        # If both fonts are now registered, make sure the font family is properly registered
        if dejavu_normal_registered and dejavu_bold_registered:
            self._validate_dejavu_font_family()
            
    def _validate_dejavu_font_family(self):
        """
        Validates that the DejaVuSans font family is properly registered with all variants.
        """
        try:
            logger.debug("Validating DejaVuSans font family registration")
            
            # Test if the font family is working by getting the mapping
            from reportlab.pdfbase.pdfmetrics import getRegisteredFontNames, _fontFamilies, registerFontFamily
            
            # Check if DejaVuSans is in font families dictionary
            if 'DejaVuSans' not in _fontFamilies:
                logger.warning("DejaVuSans font family not found, registering again")
                registerFontFamily(
                    'DejaVuSans',
                    normal='DejaVuSans',
                    bold='DejaVuSans-Bold',
                    italic='DejaVuSans',  # No italic version, use normal
                    boldItalic='DejaVuSans-Bold'  # No bold-italic, use bold
                )
                
            # Check if both fonts are in the registered font names
            registered_fonts = getRegisteredFontNames()
            if 'DejaVuSans' not in registered_fonts or 'DejaVuSans-Bold' not in registered_fonts:
                logger.error("DejaVuSans fonts not found in registered font names")
                # Fall back to standard fonts
                self._ensure_standard_fonts_available()
                
            logger.debug("DejaVuSans font family validation complete")
        except Exception as e:
            logger.error(f"Error validating DejaVuSans font family: {e}")
            # Ensure fallbacks are available
            self._ensure_standard_fonts_available()