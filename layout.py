#!/usr/bin/env python
"""
Layout - Class for managing physical layout of CV templates.
"""
from dataclasses import dataclass
from typing import Dict, Any, Tuple

from reportlab.lib.pagesizes import A4, LETTER, A3, LEGAL
from reportlab.lib.units import inch, mm


@dataclass
class Layout:
    """
    Defines physical layout parameters for the CV.
    This class manages page size, margins, and column arrangements.
    """

    # Page dimensions
    page_size: Tuple[float, float]  # (width, height)

    # Margins
    left_margin: float
    right_margin: float
    top_margin: float
    bottom_margin: float

    # Structure
    banner_height: float
    left_column_width_ratio: float  # 0-1, portion of page width

    @classmethod
    def from_dict(cls, layout_dict: Dict[str, Any]) -> 'Layout':
        """
        Create a Layout instance from a dictionary.

        Args:
            layout_dict: Dictionary containing layout settings

        Returns:
            A Layout instance with the specified settings
        """
        # Process page size
        page_size_value = layout_dict.get("page_size", "A4")
        if isinstance(page_size_value, str):
            page_size = cls._get_page_size_by_name(page_size_value)
        else:
            page_size = tuple(page_size_value)

        # Convert margin values from inches to points if they're not already
        margin_factors = {
            "left_margin": inch,
            "right_margin": inch,
            "top_margin": inch,
            "bottom_margin": inch,
            "banner_height": inch
        }

        # Convert margins from inches to points if needed
        margin_values = {}
        for key, factor in margin_factors.items():
            value = layout_dict.get(key, 0.0)
            if isinstance(value, (int, float)) and value < 10:  # Assume it's in inches if small number
                margin_values[key] = value * factor
            else:
                margin_values[key] = float(value)  # Already in points or another unit

        return cls(
            page_size=page_size,
            left_margin=margin_values.get("left_margin", 0.3 * inch),
            right_margin=margin_values.get("right_margin", 0.3 * inch),
            top_margin=margin_values.get("top_margin", 0.4 * inch),
            bottom_margin=margin_values.get("bottom_margin", 0.4 * inch),
            banner_height=margin_values.get("banner_height", 1.4 * inch),
            left_column_width_ratio=float(layout_dict.get("left_column_width_ratio", 0.3))
        )

    @staticmethod
    def _get_page_size_by_name(size_name: str) -> Tuple[float, float]:
        """
        Get page dimensions from standard page size name.

        Args:
            size_name: Name of the page size (e.g., 'A4', 'LETTER')

        Returns:
            Tuple of (width, height) in points

        Raises:
            ValueError: If the page size name is not recognized
        """
        page_sizes = {
            "A4": A4,
            "LETTER": LETTER,
            "A3": A3,
            "LEGAL": LEGAL
        }

        size_name = size_name.upper()
        if size_name in page_sizes:
            return page_sizes[size_name]
        else:
            raise ValueError(f"Unknown page size: {size_name}")

    @property
    def content_width(self) -> float:
        """Calculate the width of the content area (page width minus margins)."""
        return self.page_size[0] - self.left_margin - self.right_margin

    @property
    def content_height(self) -> float:
        """Calculate the height of the content area (page height minus margins)."""
        return self.page_size[1] - self.top_margin - self.bottom_margin

    @property
    def left_column_width(self) -> float:
        """Calculate the width of the left column."""
        return self.page_size[0] * self.left_column_width_ratio

    @property
    def right_column_width(self) -> float:
        """Calculate the width of the right column."""
        right_column_start_x = self.left_column_width
        return self.page_size[0] - right_column_start_x - self.right_margin

    @property
    def right_column_x(self) -> float:
        """Calculate the x-coordinate where the right column starts."""
        return self.left_column_width