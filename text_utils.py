#!/usr/bin/env python
"""
Text Utilities - Enhanced module for text processing operations.
Improved with better wrapping, ellipsis, and advanced text measurement.
"""
import pyphen
import re
from typing import List, Tuple, Optional, Dict

from reportlab.pdfbase.pdfmetrics import stringWidth


class TextProcessor:
    """
    Enhanced text processor with advanced wrapping and measurement capabilities.
    """

    def __init__(self, font_name: str, font_size: float, language: str = 'en_GB'):
        """
        Initialize a text processor with font settings.

        Args:
            font_name: The name of the font
            font_size: The size of the font in points
            language: The language to use for hyphenation
        """
        self.font_name = font_name
        self.font_size = font_size
        # Initialize pyphen with the specified language dictionary
        self.dic = pyphen.Pyphen(lang=language)

    def get_text_width(self, text: str) -> float:
        """
        Calculate the width of text in points using the current font settings.

        Args:
            text: The text to measure

        Returns:
            Width of the text in points
        """
        return stringWidth(text, self.font_name, self.font_size)

    def hyphenate_word(self, word: str, max_width: float, current_line_width: float) -> Tuple[Optional[str], str]:
        """
        Hyphenate a word using proper linguistic rules and find the best break point
        that fits within the available width.

        Args:
            word: Word to hyphenate
            max_width: Maximum width available
            current_line_width: Width already used on the current line

        Returns:
            Tuple of (first_part_with_hyphen, remainder) or (None, word) if no good break point
        """
        # Don't try to hyphenate very short words
        if len(word) <= 5:
            return None, word

        positions = self.dic.positions(word)
        if not positions:
            return None, word

        # Try each hyphenation point from left to right, see which best fits
        for pos in positions:
            first_part = word[:pos] + '-'
            if current_line_width + self.get_text_width(first_part) <= max_width:
                return first_part, word[pos:]

        # No good hyphenation point found
        return None, word

    def wrap_text(self, text: str, max_width: float, hyphenate: bool = True) -> List[str]:
        """
        Wrap text to fit within max_width, using linguistic hyphenation.
        Enhanced with better handling of paragraphs, punctuation, and prepositions.

        Args:
            text: Text to wrap
            max_width: Maximum width of each line
            hyphenate: Whether to use hyphenation

        Returns:
            A list of lines that fit within the specified width
        """
        if not text:
            return []

        # Split into paragraphs to preserve line breaks
        paragraphs = text.split('\n')
        result_lines = []

        for paragraph in paragraphs:
            if not paragraph.strip():
                result_lines.append('')  # Preserve empty lines
                continue

            words = paragraph.split()
            lines = []
            current_line = []
            current_width = 0
            space_width = self.get_text_width(' ')

            for i, word in enumerate(words):
                word_width = self.get_text_width(word)
                next_word = words[i + 1] if i < len(words) - 1 else None

                # If this word fits on the current line
                if current_width + (space_width if current_line else 0) + word_width <= max_width:
                    if current_line:
                        current_width += space_width
                    current_line.append(word)
                    current_width += word_width

                    # Avoid leaving single words, prepositions or articles on a line
                    if next_word and len(next_word) <= 3 and current_width + space_width + self.get_text_width(
                            next_word) > max_width:
                        # If adding this small word would cause a line break, see if we can move the current word to next line
                        if len(current_line) > 1:
                            overflow_word = current_line.pop()
                            lines.append(' '.join(current_line))
                            current_line = [overflow_word]
                            current_width = self.get_text_width(overflow_word)

                else:
                    # Word doesn't fit - try hyphenation if enabled and the word is fairly long
                    if hyphenate and len(word) > 5:
                        first_part, remainder = self.hyphenate_word(
                            word,
                            max_width,
                            current_width + (space_width if current_line else 0)
                        )
                        if first_part:  # Successful hyphenation
                            current_line.append(first_part)
                            lines.append(' '.join(current_line))
                            current_line = [remainder] if remainder else []
                            current_width = self.get_text_width(remainder) if remainder else 0
                            continue

                    # Either hyphenation wasn't possible or wasn't enabled
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
                    current_width = word_width

            # Add the last line if there's anything left
            if current_line:
                lines.append(' '.join(current_line))

            # Add this paragraph's lines to the result
            result_lines.extend(lines)

            # Add a blank line between paragraphs if this isn't the last paragraph
            if paragraph != paragraphs[-1]:
                result_lines.append('')

        # Remove any trailing empty lines
        while result_lines and not result_lines[-1]:
            result_lines.pop()

        return result_lines

    def truncate_with_ellipsis(self, text: str, max_width: float) -> str:
        """
        Truncate text to fit within max_width and add ellipsis.

        Args:
            text: Text to truncate
            max_width: Maximum width in points

        Returns:
            Truncated text with ellipsis if needed
        """
        if self.get_text_width(text) <= max_width:
            return text

        ellipsis = "..."
        ellipsis_width = self.get_text_width(ellipsis)

        if max_width <= ellipsis_width:
            return ellipsis

        # Find the maximum length that fits
        for i in range(len(text), 0, -1):
            truncated = text[:i]
            if self.get_text_width(truncated + ellipsis) <= max_width:
                return truncated + ellipsis

        return ellipsis

    def estimate_text_height(self, text: str, max_width: float, line_height: float, hyphenate: bool = True) -> float:
        """
        Estimate the height needed to render text.

        Args:
            text: Text to measure
            max_width: Maximum width for wrapping
            line_height: Height of each line
            hyphenate: Whether to use hyphenation

        Returns:
            Estimated height in points
        """
        lines = self.wrap_text(text, max_width, hyphenate)
        return len(lines) * line_height


class CanvasHelper:
    """
    Enhanced helper class for common canvas operations.
    """

    @staticmethod
    def draw_wrapped_text(
            canvas,
            text: str,
            x: float,
            y: float,
            max_width: float,
            font_name: str,
            font_size: float,
            line_height: float,
            indent: float = 0,
            hyphenate: bool = False,
            language: str = 'en_GB',
            alignment: str = 'left'
    ) -> float:
        """
        Draw wrapped text on the canvas and return the new y position.
        Enhanced with text alignment options.

        Args:
            canvas: ReportLab canvas object
            text: Text to draw
            x: X-coordinate to start drawing
            y: Y-coordinate to start drawing
            max_width: Maximum width for wrapping
            font_name: Font name
            font_size: Font size in points
            line_height: Height between lines
            indent: Indentation for each line
            hyphenate: Whether to use hyphenation
            language: Language for hyphenation
            alignment: Text alignment ('left', 'center', 'right')

        Returns:
            New y position after drawing text
        """
        processor = TextProcessor(font_name, font_size, language)
        lines = processor.wrap_text(text, max_width - indent, hyphenate=hyphenate)

        canvas.setFont(font_name, font_size)

        for line in lines:
            if not line:  # Empty line (paragraph break)
                y -= line_height
                continue

            # Calculate x position based on alignment
            if alignment == 'center':
                line_width = processor.get_text_width(line)
                line_x = x + (max_width - line_width) / 2
            elif alignment == 'right':
                line_width = processor.get_text_width(line)
                line_x = x + max_width - line_width
            else:  # 'left' alignment
                line_x = x + indent

            canvas.drawString(line_x, y, line)
            y -= line_height

        return y

    @staticmethod
    def draw_bulleted_text(
            canvas,
            bullet: str,
            text: str,
            x: float,
            y: float,
            max_width: float,
            font_name: str,
            font_size: float,
            line_height: float,
            hyphenate: bool = False,
            language: str = 'en_GB'
    ) -> float:
        """
        Draw bulleted text on the canvas and return the new y position.
        Enhanced with better handling of multi-line text.

        Args:
            canvas: ReportLab canvas object
            bullet: Bullet character or string
            text: Text to draw
            x: X-coordinate to start drawing
            y: Y-coordinate to start drawing
            max_width: Maximum width for wrapping
            font_name: Font name
            font_size: Font size in points
            line_height: Height between lines
            hyphenate: Whether to use hyphenation
            language: Language for hyphenation

        Returns:
            New y position after drawing text
        """
        # Calculate the bullet width
        canvas.setFont(font_name, font_size)
        bullet_width = stringWidth(bullet, font_name, font_size)

        # Define the text starting position (indented after the bullet)
        text_x = x + bullet_width + 5  # 5-point gap after the bullet
        text_width = max_width - (text_x - x)  # Width available for text

        # Wrap the text to fit within the available space
        processor = TextProcessor(font_name, font_size, language)
        lines = processor.wrap_text(text, text_width, hyphenate=hyphenate)

        # Draw the bullet on the first line
        canvas.drawString(x, y, bullet)

        # Draw each wrapped line of text
        for i, line in enumerate(lines):
            canvas.drawString(text_x, y, line)
            y -= line_height

            # For empty lines (paragraph breaks), don't add indentation on the next line
            if not line and i < len(lines) - 1:
                continue

        return y

    @staticmethod
    def estimate_text_block_height(
            text: str,
            max_width: float,
            font_name: str,
            font_size: float,
            line_height: float,
            hyphenate: bool = False,
            language: str = 'en_GB'
    ) -> float:
        """
        Estimate the height needed for a block of text.

        Args:
            text: Text to measure
            max_width: Maximum width for wrapping
            font_name: Font name
            font_size: Font size in points
            line_height: Height between lines
            hyphenate: Whether to use hyphenation
            language: Language for hyphenation

        Returns:
            Estimated height in points
        """
        processor = TextProcessor(font_name, font_size, language)
        lines = processor.wrap_text(text, max_width, hyphenate=hyphenate)
        return len(lines) * line_height

    @staticmethod
    def estimate_bulleted_text_height(
            text: str,
            max_width: float,
            bullet_width: float,
            font_name: str,
            font_size: float,
            line_height: float,
            hyphenate: bool = False,
            language: str = 'en_GB'
    ) -> float:
        """
        Estimate the height needed for bulleted text.

        Args:
            text: Text to measure
            max_width: Maximum width for wrapping
            bullet_width: Width of bullet and spacing
            font_name: Font name
            font_size: Font size in points
            line_height: Height between lines
            hyphenate: Whether to use hyphenation
            language: Language for hyphenation

        Returns:
            Estimated height in points
        """
        # Adjust max_width to account for bullet and spacing
        adjusted_width = max_width - bullet_width - 5  # 5-point spacing after bullet

        processor = TextProcessor(font_name, font_size, language)
        lines = processor.wrap_text(text, adjusted_width, hyphenate=hyphenate)
        return len(lines) * line_height