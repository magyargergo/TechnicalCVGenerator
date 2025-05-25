#!/usr/bin/env python
"""
Theme - Class for managing visual themes of CV templates.
"""
from dataclasses import dataclass
from typing import Dict, Any

from reportlab.lib import colors
from reportlab.lib.units import inch


@dataclass
class Theme:
    """
    Defines visual styling for the CV.
    This class manages colors, fonts, and spacing for a consistent look and feel.
    """

    # Colors
    primary_color: str  # Main brand color (e.g., banner)
    secondary_color: str  # Secondary brand color (e.g., accents)
    accent_color: str  # Highlight color (e.g., section headers)
    background_color: str  # Background color (e.g., column bg)
    text_color: str  # Main text color

    # Fonts
    header_font: str  # Font for headers
    body_font: str  # Font for body text
    header_font_size: float  # Size for headers
    body_font_size: float  # Size for body text

    # Spacing
    section_spacing: float  # Space between sections
    line_spacing: float  # Space between lines
    paragraph_spacing: float  # Space between paragraphs

    @classmethod
    def from_dict(cls, theme_dict: Dict[str, Any]) -> 'Theme':
        """
        Create a Theme instance from a dictionary.

        Args:
            theme_dict: Dictionary containing theme settings

        Returns:
            A Theme instance with the specified settings
        """
        return cls(
            # Colors
            primary_color=theme_dict.get("primary_color", "#003087"),
            secondary_color=theme_dict.get("secondary_color", "#0070CC"),
            accent_color=theme_dict.get("accent_color", "#BEDCF9"),
            background_color=theme_dict.get("background_color", "#F5F8FC"),
            text_color=theme_dict.get("text_color", "#333333"),

            # Fonts
            header_font=theme_dict.get("header_font", "Helvetica-Bold"),
            body_font=theme_dict.get("body_font", "Helvetica"),
            header_font_size=float(theme_dict.get("header_font_size", 14)),
            body_font_size=float(theme_dict.get("body_font_size", 11.5)),

            # Spacing
            section_spacing=float(theme_dict.get("section_spacing", 0.3 * inch)),
            line_spacing=float(theme_dict.get("line_spacing", 13)),
            paragraph_spacing=float(theme_dict.get("paragraph_spacing", 0.12 * inch))
        )

    def get_color(self, color_str: str, alpha=None):
        """
        Convert a color string to a ReportLab color object.

        Args:
            color_str: Color as hex string or named color
            alpha: Optional alpha value for transparency (0.0 to 1.0)

        Returns:
            ReportLab color object
        """
        if color_str.startswith("#"):
            color = colors.HexColor(color_str)
        else:
            color = getattr(colors, color_str, colors.black)
            
        # Apply transparency if specified
        if alpha is not None:
            return color.clone(alpha=alpha)
        
        return color