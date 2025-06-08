#!/usr/bin/env python
"""
Base Template - Abstract base class for CV templates with improved dynamic content handling.
"""
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple, Union

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics

from cv_data import CVData
from theme import Theme
from layout import Layout
from text_utils import TextProcessor, CanvasHelper


class BaseTemplate(ABC):
    """
    Abstract base class for all CV templates.
    Defines the interface and common functionality for templates with enhanced dynamic layout.
    """

    def __init__(self):
        """Initialize the template."""
        self.canvas = None
        self.theme = None
        self.layout = None
        self.cv_data = None
        self.profile_picture_path = None
        self.current_page = 1
        self.current_y = 0
        self.section_heights = {}  # Store pre-calculated section heights

    @abstractmethod
    def render(self, canvas: Canvas, cv_data: CVData, theme: Theme, layout: Layout,
               profile_picture_path: Optional[str] = None) -> None:
        """
        Render the CV to the canvas.

        Args:
            canvas: ReportLab canvas to draw on
            cv_data: CV data object
            theme: Theme object
            layout: Layout object
            profile_picture_path: Optional path to profile picture
        """
        self.canvas = canvas
        self.theme = theme
        self.layout = layout
        self.cv_data = cv_data
        self.profile_picture_path = profile_picture_path
        self.current_page = 1
        
        # Debug layout values
        import logging
        logger = logging.getLogger('base_template')
        logger.debug(f"BaseTemplate received layout margins: left={layout.left_margin/72:.2f}in, right={layout.right_margin/72:.2f}in, top={layout.top_margin/72:.2f}in, bottom={layout.bottom_margin/72:.2f}in")
        
        # Initialize current_y to top of content area
        self.current_y = self.layout.page_size[1] - self.layout.top_margin

        # Explicitly verify and apply fonts before rendering anything
        self._verify_fonts()
        
        # Make sure default font is properly set on the canvas
        # This should happen AFTER _verify_fonts to ensure fallbacks are in place
        self.canvas.setFont(self.theme.body_font, self.theme.body_font_size)
        
        # Save this initial state for easier restoration later
        self.canvas.saveState()

        # Pre-calculate section heights for better layout planning
        self._pre_calculate_section_heights()

    def _verify_fonts(self) -> None:
        """
        Verify that required fonts are available and usable.
        If a font isn't available, set up appropriate fallbacks.
        """
        # List of required fonts with fallbacks
        required_fonts = [
            (self.theme.header_font, "Helvetica-Bold"),
            (self.theme.body_font, "Helvetica"),
            ("FontAwesome", "Helvetica")  # For icons
        ]
        
        for font, fallback in required_fonts:
            # Test if we can get string width with this font
            try:
                test_width = self.canvas.stringWidth("Test", font, 12)
                print(f"Font verified: {font} (width of 'Test': {test_width})")
                
                # If width is 0 or very small, the font might not be properly registered
                if test_width <= 0:
                    raise Exception(f"Font '{font}' returned invalid width: {test_width}")
                    
            except Exception as e:
                print(f"Warning: Font '{font}' is not properly registered: {e}")
                print(f"Using fallback font: {fallback}")
                
                # Create font mapping to fallback
                try:
                    # Explicitly register font alias if needed
                    pdfmetrics.registerFontFamily(
                        font,
                        normal=fallback,
                        bold=fallback.replace('Helvetica', 'Helvetica-Bold') if 'Helvetica' in fallback else fallback,
                        italic=fallback.replace('Helvetica', 'Helvetica-Oblique') if 'Helvetica' in fallback else fallback,
                        boldItalic=fallback.replace('Helvetica', 'Helvetica-BoldOblique') if 'Helvetica' in fallback else fallback
                    )
                except Exception as fallback_error:
                    print(f"Error setting up fallback for {font}: {fallback_error}")
                    
        # Explicitly set the default font on the canvas again to ensure it's applied
        self.canvas.setFont(self.theme.body_font, self.theme.body_font_size)

    def _pre_calculate_section_heights(self) -> None:
        """
        Pre-calculate heights of various sections to plan layout better.
        This helps with distributing content across pages and columns.
        """
        # This method should be implemented by child classes
        pass

    def start_new_page(self) -> None:
        """Start a new page in the PDF and reset current_y position."""
        self.canvas.showPage()
        self.current_page += 1
        # Reset current_y to top of content area on new page
        self.current_y = self.layout.page_size[1] - self.layout.top_margin

        # After calling ``showPage`` ReportLab resets the graphics state which
        # results in fonts and colors falling back to defaults on the new page.
        # This caused inconsistent spacing and layout after page breaks.  Ensure
        # the theme's default font and text color are re-applied so subsequent
        # drawing commands use the expected settings.
        if self.theme is not None:
            self.canvas.setFont(self.theme.body_font, self.theme.body_font_size)
            self.canvas.setFillColor(self.theme.get_color(self.theme.text_color))

    def set_fill_color(self, color_str: str) -> None:
        """
        Set fill color from a hex string or color name.

        Args:
            color_str: Color as hex string or color name
        """
        if color_str.startswith("#"):
            self.canvas.setFillColor(colors.HexColor(color_str))
        else:
            self.canvas.setFillColor(getattr(colors, color_str, colors.black))

    def set_stroke_color(self, color_str: str) -> None:
        """
        Set stroke color from a hex string or color name.

        Args:
            color_str: Color as hex string or color name
        """
        if color_str.startswith("#"):
            self.canvas.setStrokeColor(colors.HexColor(color_str))
        else:
            self.canvas.setStrokeColor(getattr(colors, color_str, colors.black))

    def draw_section_header(
            self,
            title: str,
            x: float,
            y: float,
            width: float,
            icon: Optional[str] = None
    ) -> float:
        """
        Draw a section header with an optional icon.

        Args:
            title: Header text
            x: X-coordinate to start drawing
            y: Y-coordinate to start drawing
            width: Width of the header
            icon: Optional Font Awesome icon code

        Returns:
            New y position after drawing header
        """
        header_height = 20

        # Draw background
        self.set_fill_color(self.theme.accent_color)
        self.canvas.rect(x - 5, y - header_height, width, header_height, fill=1, stroke=0)

        # Center text vertically
        middle_y = (y - header_height) + (header_height / 2)

        # Draw icon if provided
        text_offset_x = x
        if icon:
            # Save current font settings
            current_font = self.canvas._fontname
            current_size = self.canvas._fontsize
            
            try:
                # Set color for icon
                self.set_fill_color(self.theme.text_color)
                
                # Try to use FontAwesome for the icon
                self.canvas.setFont("FontAwesome", 12)
                # Test if we can actually get a width with this font
                icon_width = self.canvas.stringWidth(icon, "FontAwesome", 12)
                
                # Only draw icon if we got a valid width
                if icon_width > 0:
                    icon_x = x
                    icon_y = middle_y - (12 / 2) + 1
                    self.canvas.drawString(icon_x, icon_y, icon)
                    text_offset_x = icon_x + icon_width + 8
                else:
                    # Fallback if stringWidth returned 0 (font not working)
                    self.canvas.setFont(self.theme.body_font, 12)
                    self.canvas.drawString(x, middle_y - 5, "•")
                    text_offset_x = x + 12
            except Exception as e:
                # Fallback: draw a bullet instead of the icon
                self.canvas.setFont(self.theme.body_font, 12)
                self.canvas.drawString(x, middle_y - 5, "•")
                text_offset_x = x + 12
                print(f"Falling back to bullet for icon, error: {e}")
            
            # Restore font settings
            self.canvas.setFont(current_font, current_size)

        # Draw title - ensure we're using the correct theme font
        self.canvas.setFont(self.theme.header_font, self.theme.header_font_size)
        self.set_fill_color(self.theme.text_color)
        text_y = middle_y - (self.theme.header_font_size / 2) + 2
        self.canvas.drawString(text_offset_x, text_y, title)

        return y - header_height

    def draw_profile_image(
            self,
            image_path: str,
            circle_center_x: float,
            circle_center_y: float,
            circle_radius: float
    ) -> None:
        """
        Draw a circular profile image.

        Args:
            image_path: Path to image file
            circle_center_x: X-coordinate of circle center
            circle_center_y: Y-coordinate of circle center
            circle_radius: Radius of circle
        """
        try:
            image = ImageReader(image_path)
            iw, ih = image.getSize()
            aspect_ratio = iw / float(ih)

            diameter = circle_radius * 2
            if aspect_ratio > 1:
                scaled_h = diameter
                scaled_w = scaled_h * aspect_ratio
            else:
                scaled_w = diameter
                scaled_h = scaled_w / aspect_ratio

            img_x = circle_center_x - scaled_w / 2
            img_y = circle_center_y - scaled_h / 2

            # Draw circular border
            self.canvas.setLineWidth(2)
            self.set_stroke_color(self.theme.secondary_color)
            self.canvas.circle(circle_center_x, circle_center_y, circle_radius, fill=0, stroke=1)

            # Clip the image to a circle and draw it
            self.canvas.saveState()
            path = self.canvas.beginPath()
            path.circle(circle_center_x, circle_center_y, circle_radius)
            self.canvas.clipPath(path, stroke=0)
            self.canvas.drawImage(image, img_x, img_y, scaled_w, scaled_h, mask='auto')
            self.canvas.restoreState()
        except Exception as e:
            print(f"Error drawing profile image: {e}")

    def calculate_text_height(
            self,
            text: str,
            max_width: float,
            font_name: Optional[str] = None,
            font_size: Optional[float] = None,
            line_height: Optional[float] = None,
            hyphenate: bool = False
    ) -> float:
        """
        Calculate the height needed to render text with the given parameters.

        Args:
            text: Text to measure
            max_width: Maximum width for wrapping
            font_name: Font name
            font_size: Font size in points
            line_height: Height between lines
            hyphenate: Whether to use hyphenation

        Returns:
            Height needed for the text in points
        """
        if font_name is None:
            font_name = self.theme.body_font
        if font_size is None:
            font_size = self.theme.body_font_size
        if line_height is None:
            line_height = self.theme.line_spacing

        processor = TextProcessor(font_name, font_size)
        lines = processor.wrap_text(text, max_width, hyphenate=hyphenate)

        # Calculate height based on number of lines and line height
        return len(lines) * line_height

    def calculate_bulleted_text_height(
            self,
            text: str,
            max_width: float,
            bullet_width: float = 10,
            font_name: Optional[str] = None,
            font_size: Optional[float] = None,
            line_height: Optional[float] = None,
            hyphenate: bool = False
    ) -> float:
        """
        Calculate the height needed for bulleted text.

        Args:
            text: Text to measure
            max_width: Maximum width for wrapping
            bullet_width: Width reserved for bullet
            font_name: Font name
            font_size: Font size in points
            line_height: Height between lines
            hyphenate: Whether to use hyphenation

        Returns:
            Height needed for the bulleted text in points
        """
        # Reduce available width to account for bullet
        adjusted_width = max_width - bullet_width
        return self.calculate_text_height(
            text, adjusted_width, font_name, font_size, line_height, hyphenate
        )

    def draw_wrapped_text(
            self,
            text: str,
            x: float,
            y: float,
            max_width: float,
            line_height: Optional[float] = None,
            indent: float = 0,
            font_name: Optional[str] = None,
            font_size: Optional[float] = None,
            hyphenate: bool = False,
            alignment: str = 'left',
            color: Optional[str] = None
    ) -> float:
        """
        Draw wrapped text and return the new y position.
        Enhanced with alignment and color options. Now supports 'justify'.

        Args:
            text: Text to draw
            x: X-coordinate to start drawing
            y: Y-coordinate to start drawing
            max_width: Maximum width for wrapping
            line_height: Height between lines
            indent: Indentation for each line
            font_name: Font name
            font_size: Font size in points
            hyphenate: Whether to use hyphenation (primarily for non-Paragraph logic)
            alignment: Text alignment ('left', 'center', 'right', 'justify')
            color: Text color (hex or name)

        Returns:
            New y position after drawing text
        """
        if font_name is None:
            font_name = self.theme.body_font
        if font_size is None:
            font_size = self.theme.body_font_size
        if line_height is None:
            line_height = self.theme.line_spacing

        original_color_obj = self.canvas._fillColorObj
        if color:
            self.set_fill_color(color)

        final_y = y

        if alignment == 'justify':
            processor = TextProcessor(font_name, font_size)
            pre_wrapped_lines = processor.wrap_text(text, max_width - indent, hyphenate=hyphenate)
            justified_text_for_paragraph = "<br/>".join(pre_wrapped_lines)

            style = ParagraphStyle(
                'justify_style',
                fontName=font_name,
                fontSize=font_size,
                leading=line_height,
                alignment=TA_JUSTIFY,
                leftIndent=indent,
            )
            if color:
                style.textColor = self.theme.get_color(color)
            else:
                style.textColor = original_color_obj

            paragraph = Paragraph(justified_text_for_paragraph, style)
            
            available_height = y
            
            p_width, p_height = paragraph.wrapOn(self.canvas, max_width, available_height)
            
            paragraph.drawOn(self.canvas, x, y - p_height) 
            final_y = y - p_height

        else:
            processor = TextProcessor(font_name, font_size)
            lines = processor.wrap_text(text, max_width - indent, hyphenate=hyphenate)
            self.canvas.setFont(font_name, font_size)

            current_y = y
            for line in lines:
                if alignment == 'center':
                    line_width = processor.get_text_width(line)
                    line_x = x + (max_width - line_width) / 2
                elif alignment == 'right':
                    line_width = processor.get_text_width(line)
                    line_x = x + max_width - line_width
                else:  # 'left' alignment
                    line_x = x + indent
                self.canvas.drawString(line_x, current_y, line)
                current_y -= line_height
            final_y = current_y

        if color:
            self.canvas.setFillColor(original_color_obj)

        return final_y

    def draw_bulleted_text(
            self,
            bullet: str,
            text: str,
            x: float,
            y: float,
            max_width: float,
            line_height: Optional[float] = None,
            font_name: Optional[str] = None,
            font_size: Optional[float] = None,
            hyphenate: bool = False,
            bullet_color: Optional[str] = None,
            text_color: Optional[str] = None
    ) -> float:
        """
        Draw bulleted text and return the new y position.
        Enhanced with color options for bullet and text.

        Args:
            bullet: Bullet character or string
            text: Text to draw
            x: X-coordinate to start drawing
            y: Y-coordinate to start drawing
            max_width: Maximum width for wrapping
            line_height: Height between lines
            font_name: Font name
            font_size: Font size in points
            hyphenate: Whether to use hyphenation
            bullet_color: Color for the bullet
            text_color: Color for the text

        Returns:
            New y position after drawing text
        """
        if font_name is None:
            font_name = self.theme.body_font
        if font_size is None:
            font_size = self.theme.body_font_size
        if line_height is None:
            line_height = self.theme.line_spacing

        # Calculate the bullet width
        self.canvas.setFont(font_name, font_size)
        bullet_width = self.canvas.stringWidth(bullet, font_name, font_size)

        # Save original color
        original_color = self.canvas._fillColorObj

        # Draw bullet with specified color
        if bullet_color:
            self.set_fill_color(bullet_color)
        self.canvas.drawString(x, y, bullet)

        # Set text color if specified
        if text_color:
            self.set_fill_color(text_color)
        elif bullet_color:  # Reset to original if only bullet had custom color
            self.canvas.setFillColor(original_color)

        # Define the text starting position (indented after the bullet)
        text_x = x + bullet_width + 5  # 5-point gap after the bullet
        text_width = max_width - (text_x - x)  # Width available for text

        # Wrap and draw the text
        processor = TextProcessor(font_name, font_size)
        lines = processor.wrap_text(text, text_width, hyphenate=hyphenate)

        # Draw each wrapped line of text
        for i, line in enumerate(lines):
            self.canvas.drawString(text_x, y, line)
            y -= line_height

        # Restore original color
        self.canvas.setFillColor(original_color)

        return y

    def check_page_break(
            self,
            y: float,
            needed_height: float,
            callback_function=None
    ) -> float:
        """
        Check if a page break is needed before drawing content.
        Enhanced with callback function for redrawing headers.

        Args:
            y: Current y position
            needed_height: Height needed for the content
            callback_function: Optional function to call after page break

        Returns:
            New y position, possibly on a new page
        """
        # Add a buffer to avoid content too close to bottom
        buffer = 15

        if y - needed_height < self.layout.bottom_margin + buffer:
            self.start_new_page()

            # Call callback function to redraw any headers/backgrounds
            if callback_function:
                callback_function()

            # Return to top of page minus top margin
            return self.layout.page_size[1] - self.layout.top_margin
        return y

    def get_remaining_page_height(self, y: float) -> float:
        """
        Calculate remaining available height on the current page.

        Args:
            y: Current y position

        Returns:
            Remaining available height in points
        """
        return y - self.layout.bottom_margin

    def truncate_text_to_fit(
            self,
            text: str,
            max_width: float,
            max_height: float,
            font_name: Optional[str] = None,
            font_size: Optional[float] = None,
            line_height: Optional[float] = None,
            add_ellipsis: bool = True
    ) -> str:
        """
        Truncate text to fit within given dimensions.

        Args:
            text: Text to truncate
            max_width: Maximum width available
            max_height: Maximum height available
            font_name: Font name
            font_size: Font size in points
            line_height: Height between lines
            add_ellipsis: Whether to add ellipsis (...) to truncated text

        Returns:
            Truncated text that fits within dimensions
        """
        if font_name is None:
            font_name = self.theme.body_font
        if font_size is None:
            font_size = self.theme.body_font_size
        if line_height is None:
            line_height = self.theme.line_spacing

        processor = TextProcessor(font_name, font_size)
        lines = processor.wrap_text(text, max_width)

        # Calculate how many lines can fit
        max_lines = int(max_height / line_height)

        if len(lines) <= max_lines:
            return text

        # If text doesn't fit, truncate to max_lines
        truncated_lines = lines[:max_lines]

        # Modify last line to add ellipsis if needed
        if add_ellipsis and max_lines > 0:
            last_line = truncated_lines[-1]
            # Find a good position to add ellipsis
            ellipsis = "..."
            ellipsis_width = processor.get_text_width(ellipsis)

            # Shorten the last line to make room for ellipsis
            while processor.get_text_width(last_line + ellipsis) > max_width and len(last_line) > 1:
                last_line = last_line[:-1]

            truncated_lines[-1] = last_line + ellipsis

        # Reconstruct text from truncated lines
        return " ".join(truncated_lines)

    def adjust_section_spacing(
            self,
            current_spacing: float,
            content_ratio: float,
            min_spacing: float,
            max_spacing: float
    ) -> float:
        """
        Dynamically adjust section spacing based on content density.

        Args:
            current_spacing: Current spacing value
            content_ratio: Ratio of content to available space (0-1)
            min_spacing: Minimum allowed spacing
            max_spacing: Maximum allowed spacing

        Returns:
            Adjusted spacing value
        """
        # If content takes up more space, reduce spacing
        # If content takes up less space, increase spacing
        if content_ratio > 0.8:  # Very dense content
            return min_spacing
        elif content_ratio < 0.4:  # Sparse content
            return max_spacing
        else:
            # Linear interpolation between min and max
            normalized_ratio = (content_ratio - 0.4) / 0.4  # Scale to 0-1
            return max_spacing - normalized_ratio * (max_spacing - min_spacing)