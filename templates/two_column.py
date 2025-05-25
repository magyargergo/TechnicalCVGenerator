#!/usr/bin/env python
"""
Two Column Template - Fixed implementation with proper color handling and positioning.
"""
import os
import logging
from typing import Dict, Any, Optional, List, Tuple, Callable

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth

from cv_data import CVData
from theme import Theme
from layout import Layout
from templates.base_template import BaseTemplate
from text_utils import TextProcessor, CanvasHelper

# Configure logging
logger = logging.getLogger('two_column_template')

class TwoColumnTemplate(BaseTemplate):
    """
    Two-column CV template with banner header.
    Fixed with proper color handling, text positioning, and layout management.
    """

    def __init__(self):
        """Initialize the template."""
        super().__init__()
        self.current_page = 1

    def render(self, canvas: Canvas, cv_data: CVData, theme: Theme, layout: Layout,
               profile_picture_path: Optional[str] = None) -> None:
        """
        Render the CV to the canvas with improved layout handling.

        Args:
            canvas: ReportLab canvas to draw on
            cv_data: CV data object
            theme: Theme object
            layout: Layout object
            profile_picture_path: Optional path to profile picture
        """
        # Preserve the original margins from layout before initializing the base class
        original_banner_height = layout.banner_height
        
        # Initialize the base class - this sets the current_y to the top margin
        super().render(canvas, cv_data, theme, layout, profile_picture_path)
        
        # Debug margins
        logger.debug(f"Layout margins: left={layout.left_margin/inch:.2f}in, right={layout.right_margin/inch:.2f}in, top={layout.top_margin/inch:.2f}in, bottom={layout.bottom_margin/inch:.2f}in")
        
        # Reset current page
        self.current_page = 1
        
        # Set debug mode from CV data
        logger.setLevel(logging.DEBUG)
        logger.debug("TwoColumnTemplate initialized in debug mode")
            
        # Draw the banner and left column background
        # This may adjust the banner height for equal spacing
        self.draw_banner_and_column_bg()
        
        # Check if banner height was adjusted and update layout accordingly
        if layout.banner_height > original_banner_height:
            logger.debug(f"Banner height was adjusted from {original_banner_height} to {layout.banner_height}")
        
        # Set up column dimensions
        page_width, page_height = self.layout.page_size
        banner_height = self.layout.banner_height

        # Left column setup
        left_col_x = self.layout.left_margin
        left_col_width = self.layout.left_column_width - self.layout.left_margin
        left_col_start_y = page_height - banner_height - self.layout.top_margin

        # Right column setup
        right_col_x = self.layout.left_column_width + (self.layout.left_margin * 0.8)
        right_col_width = page_width - right_col_x - self.layout.right_margin
        right_col_start_y = page_height - banner_height - self.layout.top_margin
        
        logger.debug(f"Page dimensions: width={page_width}, height={page_height}")
        logger.debug(f"Left column: x={left_col_x}, width={left_col_width}, start_y={left_col_start_y}")
        logger.debug(f"Right column: x={right_col_x}, width={right_col_width}, start_y={right_col_start_y}")

        # Generate the coordinated layout
        self.generate_coordinated_layout(
            left_col_x, left_col_width, left_col_start_y,
            right_col_x, right_col_width, right_col_start_y
        )

    def draw_banner_and_column_bg(self) -> None:
        """Draw the top banner with profile picture, name, and contact details, plus the left column background."""
        page_width, page_height = self.layout.page_size
        banner_height = self.layout.banner_height
        
        # Debug the dimensions being used
        logger.debug(f"Drawing banner with dimensions: width={page_width}, height={banner_height}, page_height={page_height}")
        logger.debug(f"Using margins: left={self.layout.left_margin/inch:.2f}in, right={self.layout.right_margin/inch:.2f}in, top={self.layout.top_margin/inch:.2f}in, bottom={self.layout.bottom_margin/inch:.2f}in")

        # 1) Banner bar - Force primary color
        self.canvas.setFillColor(self.theme.get_color(self.theme.primary_color))
        self.canvas.rect(
            0,
            page_height - banner_height,
            page_width,
            banner_height,
            fill=1
        )

        # 2) Profile image if available
        profile_pic_width = 0
        if self.profile_picture_path and os.path.exists(self.profile_picture_path):
            circle_radius = min(50, banner_height * 0.4)  # Increased from 40 to match larger banner
            circle_center_x = page_width - circle_radius - 25
            circle_center_y = page_height - (banner_height / 2)
            self.draw_profile_image(
                self.profile_picture_path,
                circle_center_x,
                circle_center_y,
                circle_radius
            )
            profile_pic_width = circle_radius * 2 + 50  # Account for image and spacing

        # 3) Candidate name and contact info
        candidate_data = self.cv_data.get_candidate_data()
        name = candidate_data.get("name", "")
        contact_details = candidate_data.get("contact", [])

        # Calculate contact details layout
        contact_info = self._calculate_contact_details_width(contact_details)
        
        # Center contact details horizontally in the page
        page_center_x = page_width / 2
        total_contacts_width = contact_info["total_width"]
        contact_x = page_center_x - (total_contacts_width / 2)

        # Calculate available space in banner
        # First, determine how many rows of contact details we have
        num_contact_rows = max(len(contact_info["left_col_details"]), len(contact_info["right_col_details"]))
        contact_height = num_contact_rows * 18  # Line spacing from _draw_contact_details
        
        # Determine font size for name
        name_font_size = 22
        
        # Calculate the available space for balanced spacing
        available_space = banner_height - name_font_size - contact_height
        
        # Divide space more evenly with emphasis on spacing below name and below contacts
        # Use 25% above name, 37.5% below name, and 37.5% below contacts
        padding_above_name = available_space * 0.375
        padding_below_name = available_space * 0.375
        padding_below_contacts = available_space * 0.375
        
        # Calculate vertical positions
        name_y = page_height - padding_above_name - name_font_size
        contact_y = name_y - padding_above_name - padding_below_name  # Position contacts with more padding below name

        # Draw the name
        self.canvas.setFillColor(colors.white)  # Force white color for banner text
        self.canvas.setFont(self.theme.header_font, name_font_size)
        name_width = self.canvas.stringWidth(name, self.theme.header_font, name_font_size)
        name_x = page_center_x - (name_width / 2)  # Center name in page
        self.canvas.drawString(name_x, name_y, name)

        # Draw contact details and get the bottom position
        contact_bottom_y = self._draw_contact_details(contact_y, contact_info, contact_x)
        
        # Calculate actual space used
        actual_used_height = name_y - padding_below_contacts - contact_bottom_y
        
        # Ensure the space below contacts is equal to the space below name
        required_padding_below_contacts = padding_below_contacts
        
        # Calculate required banner height to accommodate all elements with proper spacing
        required_banner_height = (page_height - name_y) + actual_used_height + required_padding_below_contacts
        
        if required_banner_height > banner_height:
            # Extend the banner if necessary
            additional_height = required_banner_height - banner_height
            banner_bottom = page_height - banner_height
            self.canvas.setFillColor(self.theme.get_color(self.theme.primary_color))
            self.canvas.rect(
                0,
                banner_bottom - additional_height,
                page_width,
                additional_height,
                fill=1,
                stroke=0
            )
            # Update banner height for other calculations
            banner_height = required_banner_height

        # 5) Left column background
        left_col_width = self.layout.left_column_width
        self.canvas.setFillColor(self.theme.get_color(self.theme.background_color))
        self.canvas.rect(0, 0, left_col_width, page_height - banner_height, fill=1, stroke=0)

    def _calculate_contact_details_width(self, contact_details: List[Dict[str, str]]) -> Dict[str, Any]:
        """Calculate the width needed for contact details to determine layout."""
        icon_font = "FontAwesome"
        icon_font_size = 10     # Match the drawing icon size
        text_font = self.theme.body_font
        text_font_size = 9.5    # Match the drawing text size
        icon_padding = 6        # Match the drawing padding
        column_gap = 35         # Match the drawing column gap

        # Limit to a reasonable number of contact details to avoid overflow
        max_details = 6
        if len(contact_details) > max_details:
            contact_details = contact_details[:max_details]

        # Calculate how many items per column for balanced layout
        half = (len(contact_details) + 1) // 2
        left_col_details = contact_details[:half]
        right_col_details = contact_details[half:]

        def measure_line(icon_code: str, text: str) -> float:
            icon_w = self.canvas.stringWidth(icon_code, icon_font, icon_font_size)

            # Truncate text if too long
            max_text_width = 220  # Increased for better proportion
            text_w = self.canvas.stringWidth(text, text_font, text_font_size)

            if text_w > max_text_width:
                # Truncate and add ellipsis
                processor = TextProcessor(text_font, text_font_size)
                text = processor.truncate_with_ellipsis(text, max_text_width)
                text_w = self.canvas.stringWidth(text, text_font, text_font_size)

            return icon_w + icon_padding + text_w

        # Find the widest line in each column
        left_col_width = max((measure_line(d["icon"], d["text"]) for d in left_col_details), default=0)
        right_col_width = max((measure_line(d["icon"], d["text"]) for d in right_col_details), default=0)

        # Process each detail text for potential truncation
        truncated_details = {}
        for detail in contact_details:
            icon = detail["icon"]
            text = detail["text"]
            
            # Special truncation for URLs (http/https links)
            if text.startswith(("http://", "https://", "www.")):
                # For URLs, we can be more aggressive with truncation since they're clickable
                max_url_width = 160  # Shorter width specifically for URLs
                text_width = self.canvas.stringWidth(text, text_font, text_font_size)
                
                if text_width > max_url_width:
                    # Keep the beginning of the URL (scheme and domain)
                    parts = text.split('/')
                    if len(parts) >= 3:  # Has at least scheme://domain
                        domain_part = parts[2].split('.')
                        if len(domain_part) > 2:  # Subdomain like www.example.com
                            domain = '.'.join(domain_part[-2:])  # Keep example.com
                        else:
                            domain = '.'.join(domain_part)  # Keep as is
                            
                        truncated_text = f"{parts[0]}//{domain}/..."
                    else:
                        # Fallback to standard truncation
                        processor = TextProcessor(text_font, text_font_size)
                        truncated_text = processor.truncate_with_ellipsis(text, max_url_width)
                    
                    truncated_details[icon] = truncated_text
                else:
                    truncated_details[icon] = text
            else:
                # Standard truncation for non-URL text
                max_width = 220  # Standard width for non-URL text
                text_width = self.canvas.stringWidth(text, text_font, text_font_size)

                if text_width > max_width:
                    processor = TextProcessor(text_font, text_font_size)
                    truncated_text = processor.truncate_with_ellipsis(text, max_width)
                    truncated_details[icon] = truncated_text
                else:
                    truncated_details[icon] = text

        total_width = left_col_width + right_col_width + column_gap

        return {
            "left_col_details": left_col_details,
            "right_col_details": right_col_details,
            "truncated_details": truncated_details,
            "left_col_width": left_col_width,
            "right_col_width": right_col_width,
            "column_gap": column_gap,
            "total_width": total_width
        }

    def _draw_contact_details(self, initial_y: float, contact_info: Dict[str, Any], start_x: float) -> float:
        """Draw contact details in two columns with improved spacing and text handling."""
        self.canvas.setFillColor(colors.white)  # Force white color for banner text

        icon_font = "FontAwesome"
        icon_font_size = 10     # Reduced from 11
        text_font = self.theme.body_font
        text_font_size = 9.5    # Reduced from 10.5
        line_spacing = 18       # Reduced from 20
        icon_padding = 6        # Reduced from 7

        left_col_details = contact_info["left_col_details"]
        right_col_details = contact_info["right_col_details"]
        left_col_width = contact_info["left_col_width"]
        column_gap = 35         # Reduced from 40
        truncated_details = contact_info["truncated_details"]

        # Draw a subtle separator between columns if there are items in both columns
        if left_col_details and right_col_details:
            # Calculate separator position - center it on the page width
            page_width = self.layout.page_size[0]
            separator_x = page_width / 2  # Exact center of page
            separator_top = initial_y + 10
            separator_bottom = initial_y - (max(len(left_col_details), len(right_col_details)) * line_spacing)
            
            # Draw vertical separator with subtle color
            self.canvas.setStrokeColor(colors.white.clone(alpha=0.3))  # Semi-transparent white
            self.canvas.setLineWidth(0.5)
            self.canvas.line(separator_x, separator_top, separator_x, separator_bottom)

        # Left column
        current_y_left = initial_y
        for detail in left_col_details:
            icon_code = detail["icon"]
            text = truncated_details[icon_code]

            # Draw icon with slight offset for visual alignment
            self.canvas.setFont(icon_font, icon_font_size)
            self.canvas.drawString(start_x, current_y_left + 1, icon_code)  # +1 for slight vertical alignment

            # Draw text with proper spacing
            self.canvas.setFont(text_font, text_font_size)
            text_x = start_x + icon_padding + self.canvas.stringWidth(icon_code, icon_font, icon_font_size)
            self.canvas.drawString(text_x, current_y_left, text)

            current_y_left -= line_spacing

        # Right column
        current_y_right = initial_y
        # Calculate right column position based on centered divider
        right_col_x = separator_x + (column_gap / 2)  # Position right column based on centered divider

        for detail in right_col_details:
            icon_code = detail["icon"]
            text = truncated_details[icon_code]

            # Draw icon with slight offset for visual alignment
            self.canvas.setFont(icon_font, icon_font_size)
            self.canvas.drawString(right_col_x, current_y_right + 1, icon_code)  # +1 for slight vertical alignment

            # Draw text with proper spacing
            self.canvas.setFont(text_font, text_font_size)
            text_x = right_col_x + icon_padding + self.canvas.stringWidth(icon_code, icon_font, icon_font_size)
            self.canvas.drawString(text_x, current_y_right, text)

            current_y_right -= line_spacing

        # Reset font and color for subsequent content
        self.canvas.setFont(self.theme.body_font, self.theme.body_font_size)
        self.set_fill_color(self.theme.text_color)
        
        # Return the bottom y-position of the contact details
        return min(current_y_left, current_y_right)

    def generate_coordinated_layout(
            self,
            left_col_x: float,
            left_col_width: float,
            left_y: float,
            right_col_x: float,
            right_col_width: float,
            right_y: float
    ) -> None:
        """
        Build the left and right columns independently, but ensure the first
        sections (TECHNICAL EXPERTISE and PROFILE) start at the same vertical
        position for visual balance.

        After the first sections, each column handles its own page-breaks with 
        `check_page_break`, and logical blocks are kept together by estimating
        their heights inside the individual section methods.
        """
        logger.debug("=== GENERATING LAYOUT WITH BALANCED TOP SECTIONS ===")

        page_height = self.layout.page_size[1]
        content_top_y = page_height - self.layout.banner_height - self.layout.top_margin
        
        # Save the initial starting Y for both columns to ensure alignment
        initial_start_y = left_y
        
        # -------------------------------------------------------------------
        # ALIGNED TOP SECTIONS (Technical Skills and Profile must align)
        # -------------------------------------------------------------------
        logger.debug("-- Rendering TOP sections in alignment --")
        logger.debug(f"Initial top position for both columns: y={initial_start_y:.2f}")
        
        # Draw the first sections in both columns at the same starting Y
        left_y_after_skills = self.add_technical_skills_section(left_col_x, left_col_width, initial_start_y)
        right_y_after_profile = self.add_profile_section(right_col_x, right_col_width, initial_start_y)
        
        logger.debug(f"After aligned top sections - Left(Technical Skills): y={left_y_after_skills:.2f}, Right(Profile): y={right_y_after_profile:.2f}")
        
        # ------------------------------------------------------------------
        # CONTINUE LEFT COLUMN independently (education, more details)
        # ------------------------------------------------------------------
        logger.debug("-- Continuing LEFT column sections independently --")
        left_current_y = left_y_after_skills
        left_current_y = self.add_education_section(left_col_x, left_col_width, left_current_y)
        left_current_y = self.add_more_details_section(left_col_x, left_col_width, left_current_y)
        logger.debug(f"LEFT column finished on page {self.current_page} at y={left_current_y:.2f}")

        # Save what page we're on after the left column
        current_page_after_left = self.current_page

        # ------------------------------------------------------------------
        # CONTINUE RIGHT COLUMN independently (experience, projects, references)
        # ------------------------------------------------------------------
        logger.debug("-- Continuing RIGHT column sections independently --")
        # Handle if the left column caused page breaks (we're now on a new page)
        if self.current_page > 1 and current_page_after_left > 1:
            # If we're on a new page due to left column page breaks,
            # reset right column to start at the top of the current page
            right_current_y = content_top_y
            logger.debug(f"Left column moved to page {current_page_after_left}, starting right column from top: y={right_current_y:.2f}")
        else:
            # Otherwise continue from where Profile ended
            right_current_y = right_y_after_profile
        
        right_current_y = self.add_experience_section(right_col_x, right_col_width, right_current_y)
        right_current_y = self.add_projects_section(right_col_x, right_col_width, right_current_y)

        logger.debug(f"RIGHT column finished on page {self.current_page} at y={right_current_y:.2f}")
        logger.debug("=== BALANCED LAYOUT COMPLETE ===")
        logger.debug(f"Total pages: {self.current_page}")

    def draw_multiline_section_header(
            self,
            title_lines: List[str],
            x: float,
            y: float,
            width: float,
            icon: Optional[str] = None
    ) -> float:
        """
        Draw a section header with multiple lines and an optional icon.

        Args:
            title_lines: List of lines for the header
            x: X-coordinate to start drawing
            y: Y-coordinate to start drawing
            width: Width of the header
            icon: Optional Font Awesome icon code

        Returns:
            New y position after drawing header
        """
        # Calculate height based on number of lines
        line_count = len(title_lines)
        line_height = self.theme.line_spacing
        header_height = line_count * line_height + 10  # 5 pixels padding top and bottom

        # Draw background with accent color
        self.canvas.setFillColor(self.theme.get_color(self.theme.accent_color))
        self.canvas.rect(x - 5, y - header_height + 8, width, header_height, fill=1, stroke=0)

        # Calculate icon position - centered vertically
        if icon:
            self.canvas.setFont("FontAwesome", 12)
            icon_width = self.canvas.stringWidth(icon, "FontAwesome", 12)
            icon_x = x
            # Position icon at center of the multiline header
            icon_y = y - (header_height / 2) + 4  # Adjust for better vertical alignment
            self.canvas.setFillColor(self.theme.get_color(self.theme.text_color))
            self.canvas.drawString(icon_x, icon_y, icon)
            text_offset_x = icon_x + icon_width + 8
        else:
            text_offset_x = x

        # Draw each line of the title
        self.canvas.setFont(self.theme.header_font, self.theme.header_font_size)
        self.canvas.setFillColor(self.theme.get_color(self.theme.text_color))

        for i, line in enumerate(title_lines):
            # Calculate vertical position for each line
            line_y = y - (i + 1) * line_height + 5  # +5 for some extra padding from top
            self.canvas.drawString(text_offset_x, line_y, line)

        return y - header_height

    def add_technical_skills_section(self, x: float, width: float, start_y: float) -> float:
        """Add Technical Expertise section to the left column."""
        # Skip if no technical skills
        if not self.cv_data.has_section("technical_skills"):
            return start_y

        skills_data = self.cv_data.get_technical_skills()
        section_icon = "\uf085"  # Cogs icon

        # Use a multiline section header for "TECHNICAL EXPERTISE"
        y = self.draw_section_header("TECHNICAL EXPERTISE", x, start_y, width, section_icon, multiline=True)
        y -= self.theme.line_spacing * 1.5

        for category, skills in skills_data.items():
            # Check if we need a page break for this category
            category_height = self.theme.line_spacing * 1.2  # Category heading
            skills_height = sum(self.calculate_bulleted_text_height(skill, width - 10, self.theme.line_spacing * 0.8)
                                for skill in skills)
            total_height = category_height + skills_height + self.theme.line_spacing * 1.2

            y = self.check_page_break(y, total_height, self.draw_banner_and_column_bg)

            # Category header - Ensure proper color
            self.canvas.setFont(self.theme.header_font, self.theme.body_font_size)
            self.canvas.setFillColor(self.theme.get_color(self.theme.text_color))
            self.canvas.drawString(x + 5, y, category)
            y -= self.theme.line_spacing * 1.2

            # Skills - Ensure proper text color
            for skill in skills:
                y = self.draw_bulleted_text(
                    bullet="•",
                    text=skill,
                    x=x + 10,
                    y=y,
                    max_width=width - 10,
                    hyphenate=True,
                    text_color=self.theme.text_color
                )
                y -= self.theme.line_spacing * 0.4

            y -= self.theme.line_spacing * 0.8

        return y - self.theme.section_spacing

    def add_education_section(self, x: float, width: float, start_y: float) -> float:
        """Add Education section to the left column with improved color handling."""
        # Skip if no education data
        if not self.cv_data.has_section("education"):
            return start_y

        education_data = self.cv_data.get_education_data()
        section_icon = "\uf19d"  # Graduation cap icon
        
        logger.debug(f"=== STARTING EDUCATION SECTION === at y={start_y:.2f}")
        
        # First check if all education items can fit on the current page
        total_height = 0
        # Height of section header
        header_height = 20 + self.theme.line_spacing * 1.2
        total_height += header_height
        
        # Calculate total height for all education items
        all_items_height = 0
        for edu in education_data.get("items", []):
            item_height = self._estimate_education_item_height(edu, width)
            all_items_height += item_height
        
        total_height += all_items_height
        total_height += self.theme.section_spacing * 0.8  # Final spacing
        
        available_height = start_y - self.layout.bottom_margin - 5  # 5pt buffer
        
        # If it won't fit on current page, start a new page
        if total_height > available_height:
            logger.debug(f"Education section total height ({total_height:.2f}) exceeds available space ({available_height:.2f}). Starting new page.")
            self.start_new_page()
            self.draw_banner_and_column_bg()
            y = self.layout.page_size[1] - self.layout.banner_height - self.layout.top_margin
        else:
            y = start_y
        
        # Draw section header
        y = self.draw_section_header("EDUCATION", x, y, width, section_icon)
        y -= self.theme.line_spacing * 1.2  # Slightly reduced from 1.5
        
        logger.debug(f"After education header, y={y:.2f}")
        
        # Now draw each education item
        for i, edu in enumerate(education_data.get("items", [])):
            # Get the height needed for this item
            needed_height = self._estimate_education_item_height(edu, width)
            
            institution = edu.get("institution", "")
            logger.debug(f"Education item #{i+1}: {institution}")
            logger.debug(f"  Estimated height: {needed_height:.2f}, Current y: {y:.2f}")
            
            # If this single item won't fit on the current page, start a new page
            # This prevents splitting a single education item across pages
            if y - needed_height < self.layout.bottom_margin + 5:  # 5pt buffer
                logger.debug(f"  Education item won't fit on current page. Starting new page.")
                self.start_new_page()
                self.draw_banner_and_column_bg()
                
                # Redraw the section header on the new page
                y = self.layout.page_size[1] - self.layout.banner_height - self.layout.top_margin
                y = self.draw_section_header("EDUCATION", x, y, width, section_icon)
                y -= self.theme.line_spacing * 1.2
                
                logger.debug(f"  Continuing on new page. New y={y:.2f}")

            # Institution with proper color and improved wrapping for long names
            institution = edu.get("institution", "")
            # Force wrapping for very long institution names by calculating if name is too long for width
            inst_width = self.canvas.stringWidth(institution, self.theme.header_font, self.theme.body_font_size)
            max_width_for_inst = width - 5  # Slightly reduced width for better fit
            
            logger.debug(f"  Institution: '{institution}'")
            logger.debug(f"  Institution width: {inst_width:.2f}, Max width: {max_width_for_inst:.2f}")
            logger.debug(f"  Will{' ' if inst_width > max_width_for_inst else ' not '}need wrapping")
            
            # If institution name is too long, use wrapped text drawing
            y = self.draw_wrapped_text(
                text=institution,
                x=x,
                y=y,
                max_width=max_width_for_inst,
                indent=5,
                font_name=self.theme.header_font,
                font_size=self.theme.body_font_size,
                hyphenate=True,
                color=self.theme.text_color
            )
            y -= self.theme.line_spacing * 0.4
            
            logger.debug(f"  After institution name, y={y:.2f}")

            details = [edu.get("degree", ""), edu.get("duration", "")]
            for j, detail in enumerate(details):
                if detail:  # Only draw if there's something to draw
                    logger.debug(f"  Detail #{j+1}: '{detail}'")
                        
                    y = self.draw_wrapped_text(
                        text=detail,
                        x=x,
                        y=y,
                        max_width=width - 10,  # Reduced width for better margin
                        indent=10,
                        hyphenate=True,
                        color=self.theme.text_color
                    )
                    y -= self.theme.line_spacing * 0.5
                    
                    logger.debug(f"  After detail #{j+1}, y={y:.2f}")

            y -= self.theme.paragraph_spacing * 0.4  # Further reduced for tighter layout
            
            logger.debug(f"  After education item #{i+1}, y={y:.2f}")
            logger.debug(f"  Remaining space: {y - self.layout.bottom_margin:.2f}")

        final_y = y - self.theme.section_spacing * 0.8  # Slightly reduced
        
        logger.debug(f"=== FINISHED EDUCATION SECTION === Final y={final_y:.2f}")
            
        return final_y

    def _estimate_education_item_height(self, edu: Dict[str, str], width: float) -> float:
        """Estimate the height needed for an education item."""
        institution = edu.get("institution", "")
        degree = edu.get("degree", "")
        duration = edu.get("duration", "")

        height = 0

        # Institution
        height += self.calculate_text_height(
            institution,
            width,
            self.theme.header_font,
            self.theme.body_font_size
        ) + self.theme.line_spacing * 0.4

        # Degree and duration
        if degree:
            height += self.calculate_text_height(
                degree,
                width - 5,
                self.theme.body_font,
                self.theme.body_font_size
            ) + self.theme.line_spacing * 0.5

        if duration:
            height += self.calculate_text_height(
                duration,
                width - 5,
                self.theme.body_font,
                self.theme.body_font_size
            ) + self.theme.line_spacing * 0.5

        height += self.theme.paragraph_spacing * 0.4

        return height

    def add_more_details_section(self, x: float, width: float, start_y: float) -> float:
        """Add More Details section to the left column with improved color handling."""
        additional_info = self.cv_data.get_additional_info()
        if not additional_info:
            return start_y

        section_icon = "\uf05a"  # Info icon

        y = self.draw_section_header("MORE DETAILS", x, start_y, width, section_icon)
        y -= self.theme.line_spacing * 1.5

        for info in additional_info:
            # Check for page break
            needed_height = self.calculate_bulleted_text_height(info, width - 10)
            y = self.check_page_break(y, needed_height, self.draw_banner_and_column_bg)

            y = self.draw_bulleted_text(
                bullet="•",
                text=info,
                x=x + 10,
                y=y,
                max_width=width - 10,
                hyphenate=True,
                text_color=self.theme.text_color
            )
            y -= self.theme.line_spacing * 0.6

        return y - self.theme.section_spacing

    def add_profile_section(self, x: float, width: float, start_y: float) -> float:
        """Add Profile section to the right column with improved color handling."""
        profile_text = self.cv_data.get_profile_data()
        if not profile_text:
            return start_y

        section_icon = "\uf007"  # User icon

        y = self.draw_section_header("PROFILE", x, start_y, width, section_icon)
        y -= self.theme.line_spacing * 1.5

        # Split the profile text into paragraphs
        paragraphs = profile_text.split('\n\n')

        for paragraph in paragraphs:
            # Check for page break
            paragraph_height = self.calculate_text_height(
                paragraph,
                width,
                line_height=self.theme.line_spacing * 1.3
            )
            y = self.check_page_break(y, paragraph_height, self.draw_banner_and_column_bg)

            y = self.draw_wrapped_text(
                text=paragraph,
                x=x,
                y=y,
                max_width=width,
                line_height=self.theme.line_spacing * 1.3,
                indent=5,
                hyphenate=True, # Hyphenation will be attempted by TextProcessor before Paragraph
                alignment='justify', # Justify profile paragraphs
                color=self.theme.text_color
            )
            y -= self.theme.line_spacing * 1.2  # Extra space between paragraphs

        return y - self.theme.paragraph_spacing * 0.5

    def add_experience_section(self, x: float, width: float, start_y: float) -> float:
        """Add Professional Experience section with more organic page breaks for roles."""
        experience_data = self.cv_data.get_experience_data()
        if not experience_data or not experience_data.get("companies"):
            return start_y

        section_icon = "\uf0b1"  # Briefcase icon
        current_y = start_y
        logger.debug(f"=== STARTING EXPERIENCE SECTION === at y={current_y:.2f} on Page {self.current_page}")
        
        # Draw section header
        current_y = self.draw_section_header("PROFESSIONAL EXPERIENCE", x, current_y, width, section_icon)
        current_y -= self.theme.line_spacing 
        logger.debug(f"  After Exp header, y={current_y:.2f}. Space left on page: {current_y - self.layout.bottom_margin:.2f}")
        
        companies = experience_data.get("companies", [])
        for i, company in enumerate(companies):
            company_name = company.get("name", "")
            
            # Estimate full height for this company including all roles
            company_height = self._estimate_company_height(company, width)
            logger.debug(f"  Company #{i+1}: {company_name} (Est. total height: {company_height:.2f})")
            
            # If this company won't fit entirely on current page, start a new page
            if current_y - company_height < self.layout.bottom_margin + 5:  # 5pt buffer
                logger.debug(f"    Company '{company_name}' won't fit on current page. Starting new page.")
                self.start_new_page()
                self.draw_banner_and_column_bg()
                
                # Redraw the section header on the new page
                current_y = self.layout.page_size[1] - self.layout.banner_height - self.layout.top_margin
                current_y = self.draw_section_header("PROFESSIONAL EXPERIENCE", x, current_y, width, section_icon)
                current_y -= self.theme.line_spacing
                
                logger.debug(f"    Continuing on new page {self.current_page}. New y={current_y:.2f}")
            
            # Now draw the company header
            start_date = company.get("startDate", "")
            
            # Calculate end date: 
            # - Use "Present" for the first company (latest experience)
            # - For other companies, calculate based on isCurrent flag or use provided endDate
            if i == 0:
                end_date = "Present"
            else:
                # Check if the company has a flag indicating it's a current role
                is_current = company.get("isCurrent", False)
                if is_current:
                    end_date = "Present"
                else:
                    end_date = company.get("endDate", "")
                
            date_range = f"{start_date} - {end_date}" if start_date else ""
            company_line = f"{company_name} | {date_range}"
            
            current_y = self.draw_wrapped_text(
                text=company_line, x=x, y=current_y, max_width=width, indent=5,
                font_name=self.theme.header_font, font_size=self.theme.body_font_size,
                hyphenate=True, color=self.theme.primary_color)
            current_y -= self.theme.line_spacing * 0.6
            logger.debug(f"    After company header '{company_name}', y={current_y:.2f}")

            # Draw roles within the company
            for j, role in enumerate(company.get("roles", [])):
                role_title = role.get("title", "")
                responsibilities = role.get("responsibilities", [])
                
                logger.debug(f"      Role #{j+1}: {role_title}")
                
                # Draw Role Title
                current_y = self.draw_wrapped_text(
                    text=role_title, x=x, y=current_y, max_width=width, indent=10,
                    font_name=self.theme.body_font, font_size=self.theme.body_font_size,
                    hyphenate=True, color=self.theme.secondary_color)
                current_y -= self.theme.line_spacing * 0.5
                logger.debug(f"        After role title '{role_title}', y={current_y:.2f}")

                # Draw Responsibilities for this role
                for k, resp_text in enumerate(responsibilities):
                    current_y = self.draw_bulleted_text(
                        bullet="•", text=resp_text, x=x + 15, y=current_y,
                        max_width=width - 15, hyphenate=True, text_color=self.theme.text_color)
                    current_y -= self.theme.line_spacing * 0.2
                
                if responsibilities: # Add spacing only if there were responsibilities
                    current_y -= self.theme.line_spacing * 0.6 # Space after all responsibilities for a role
                logger.debug(f"        After responsibilities for '{role_title}', y={current_y:.2f}")

            current_y -= self.theme.paragraph_spacing * 0.4 
            logger.debug(f"    After company '{company_name}', y={current_y:.2f}. Space left: {current_y - self.layout.bottom_margin:.2f}")

        logger.debug(f"=== FINISHED EXPERIENCE SECTION === Final y={current_y:.2f} on Page {self.current_page}")
        return current_y

    def _estimate_company_height(self, company: Dict[str, Any], width: float) -> float:
        """
        Estimate the height needed to render a company section.
        Used for page break calculations.

        Args:
            company: Company data
            width: Available width

        Returns:
            Estimated height in points
        """
        # More accurate height estimation
        line_height = self.theme.line_spacing

        # Company name and date range (with calculated end date)
        start_date = company.get('startDate', '')
        
        # Calculate end date following same logic as in rendering
        is_current = company.get('isCurrent', False)
        if is_current:
            end_date = "Present"
        else:
            end_date = company.get('endDate', '')
            
        date_range = f"{start_date} - {end_date}" if start_date else ""
        company_line = f"{company.get('name', '')} | {date_range}"
        company_header_height = self.calculate_text_height(
            company_line,
            width,
            self.theme.header_font,
            self.theme.body_font_size
        ) + line_height * 0.7  # Slightly reduce padding

        total_height = company_header_height

        for role in company.get("roles", []):
            # Role title
            role_title_height = self.calculate_text_height(
                role.get("title", ""),
                width, # Role title can use full width before indent
                self.theme.body_font,
                self.theme.body_font_size
            ) + line_height * 0.6  # Slightly reduce padding

            # Responsibilities
            responsibilities = role.get("responsibilities", [])
            responsibilities_height = 0

            # Use a smaller width for bulleted responsibilities due to indent
            resp_width = width - 15 # Standard indent for responsibilities

            for resp in responsibilities: # Estimate all responsibilities
                resp_height = self.calculate_bulleted_text_height(resp, resp_width) 
                responsibilities_height += resp_height + line_height * 0.2  # Minimal spacing between resp lines

            total_height += role_title_height + responsibilities_height + line_height * 0.6  # Slightly reduce padding

        # Slightly reduce the final padding
        total_height += self.theme.paragraph_spacing * 0.4  # Further reduced for tighter layout
        
        return total_height

    def _estimate_project_height(self, project: Dict[str, Any], width: float) -> float:
        """Estimate the height needed for a single project item."""
        title = project.get("title", "")
        description = project.get("description", "")
        height = 0

        # Project title - similar to company name in experience section
        height += self.calculate_text_height(
            title,
            width, # Title uses full width before indent
            self.theme.header_font,
            self.theme.body_font_size
        ) + self.theme.line_spacing * 0.6 # Match company spacing

        # Project description - similar to responsibilities in experience section
        desc_width = width - 10 # Accounting for indent
        height += self.calculate_text_height(
            description,
            desc_width,
            self.theme.body_font,
            self.theme.body_font_size,
            line_height=self.theme.line_spacing
        )

        # Add space after project - similar to after company in experience
        height += self.theme.paragraph_spacing * 0.4

        return height

    def add_projects_section(self, x: float, width: float, start_y: float) -> float:
        """Add Projects & Achievements section with organic page breaks."""
        projects_data = self.cv_data.get_projects_data()
        if not projects_data:
            return start_y

        section_icon = "\uf0ae"  # Tasks icon
        current_y = start_y
        logger.debug(f"=== STARTING PROJECTS SECTION === at y={current_y:.2f} on Page {self.current_page}")
        
        # Draw the section header - match Experience section
        current_y = self.draw_section_header("PROJECTS & ACHIEVEMENTS", x, current_y, width, section_icon)
        current_y -= self.theme.line_spacing  # Same spacing as Experience section
        section_header_drawn = True  # Track if section header is drawn on current page
        
        for i, project in enumerate(projects_data):
            title = project.get("title", "")
            description = project.get("description", "")
            
            logger.debug(f"  Project #{i+1}: {title}")
            
            # Estimate height for this project
            project_height = self._estimate_project_height(project, width)
            logger.debug(f"    Estimated height: {project_height:.2f}, Current y: {current_y:.2f}, Page: {self.current_page}")

            # If this project won't fit on current page, start a new page
            if current_y - project_height < self.layout.bottom_margin + 5:  # 5pt buffer
                logger.debug(f"    Project '{title}' won't fit on current page. Starting new page.")
                self.start_new_page()
                self.draw_banner_and_column_bg()
                
                # Redraw section header on new page ONLY if this is the first project
                current_y = self.layout.page_size[1] - self.layout.banner_height - self.layout.top_margin
                if i == 0:
                    current_y = self.draw_section_header("PROJECTS & ACHIEVEMENTS", x, current_y, width, section_icon)
                    current_y -= self.theme.line_spacing  # Match experience section
                
                section_header_drawn = True
                
                logger.debug(f"    Continuing on new page {self.current_page}. New y={current_y:.2f}")

            # Project title with primary color - using same style as company names in Experience section
            current_y = self.draw_wrapped_text(
                text=title, x=x, y=current_y, max_width=width, indent=5,
                font_name=self.theme.header_font, font_size=self.theme.body_font_size,
                hyphenate=True, color=self.theme.primary_color)
            current_y -= self.theme.line_spacing * 0.6  # Match company spacing
            logger.debug(f"    After project title '{title}', y={current_y:.2f}")

            # Project description - treat similar to responsibilities in Experience section
            current_y = self.draw_wrapped_text(
                text=description, x=x + 10, y=current_y, max_width=width - 10, indent=5,
                font_name=self.theme.body_font, font_size=self.theme.body_font_size,
                hyphenate=True,
                color=self.theme.text_color
            )
            
            # Add similar spacing to what comes after a company in the Experience section
            current_y -= self.theme.paragraph_spacing * 0.4
            logger.debug(f"    After project description, y={current_y:.2f}. Remaining space: {current_y - self.layout.bottom_margin:.2f}")

        # Add references if available
        references = self.cv_data.get_references()
        if references:
            # Calculate height needed for references section
            ref_header_height = 20 + self.theme.line_spacing * 1.2
            ref_text_height = self.calculate_text_height(references, width - 5)
            total_ref_height = ref_header_height + ref_text_height
            
            # Check if references will fit on current page
            if current_y - total_ref_height < self.layout.bottom_margin + 5:  # 5pt buffer
                logger.debug(f"  References won't fit on current page. Starting new page.")
                self.start_new_page()
                self.draw_banner_and_column_bg()
                current_y = self.layout.page_size[1] - self.layout.banner_height - self.layout.top_margin
                section_header_drawn = False
            
            current_y = self.draw_section_header("REFERENCES", x, current_y, width, "\uf0c0")  # Users icon
            current_y -= self.theme.line_spacing  # Match experience section

            current_y = self.draw_wrapped_text(
                text=references, x=x, y=current_y, max_width=width, indent=5,
                hyphenate=False, # References are usually short, no need to justify
                alignment='left', # Keep references left-aligned
                color=self.theme.text_color)
            logger.debug(f"  After References, y={current_y:.2f}")

        logger.debug(f"=== FINISHED PROJECTS SECTION === Final y={current_y:.2f} on Page {self.current_page}")
        return current_y

    def draw_section_header(
            self,
            title: str,
            x: float,
            y: float,
            width: float,
            icon: Optional[str] = None,
            multiline: bool = False
    ) -> float:
        """
        Draw a section header with an optional icon.
        Enhanced to support multiline titles.

        Args:
            title: Header text
            x: X-coordinate to start drawing
            y: Y-coordinate to start drawing
            width: Width of the header
            icon: Optional Font Awesome icon code
            multiline: Whether to split title into multiple lines

        Returns:
            New y position after drawing header
        """
        if multiline and " " in title:
            # Split the title at a space for multiline display
            parts = title.split(" ", 1)
            return self.draw_multiline_section_header(parts, x, y, width, icon)
        else:
            # Standard single-line header
            header_height = 20

            # Draw background
            self.canvas.setFillColor(self.theme.get_color(self.theme.accent_color))
            self.canvas.rect(x - 5, y - header_height, width, header_height, fill=1, stroke=0)

            # Center text vertically
            middle_y = (y - header_height) + (header_height / 2)

            # Draw icon if provided
            if icon:
                self.canvas.setFont("FontAwesome", 12)
                icon_width = self.canvas.stringWidth(icon, "FontAwesome", 12)
                icon_x = x
                icon_y = middle_y - (12 / 2) + 1
                self.canvas.setFillColor(self.theme.get_color(self.theme.text_color))
                self.canvas.drawString(icon_x, icon_y, icon)
                text_offset_x = icon_x + icon_width + 8
            else:
                text_offset_x = x

            # Draw title
            self.canvas.setFont(self.theme.header_font, self.theme.header_font_size)
            self.canvas.setFillColor(self.theme.get_color(self.theme.text_color))
            text_y = middle_y - (self.theme.header_font_size / 2) + 2
            self.canvas.drawString(text_offset_x, text_y, title)

            return y - header_height

    def check_page_break(self, y: float, needed_height: float, redraw_function: Optional[Callable] = None) -> float:
        """
        Check if a page break is needed before drawing content.
        Enhanced with callback for redrawing headers.

        Args:
            y: Current y position
            needed_height: Height needed for the content
            redraw_function: Function to call after page break

        Returns:
            New y position, possibly on a new page
        """
        # Use a minimal buffer to maximize space usage
        buffer = 5  # Reduced from 15
        
        logger.debug(f"Checking page break - Current y: {y:.2f}, Needed height: {needed_height:.2f}")
        logger.debug(f"Bottom margin: {self.layout.bottom_margin:.2f}, Buffer: {buffer}")
        logger.debug(f"Space available: {y - self.layout.bottom_margin:.2f}")
        logger.debug(f"Space needed: {needed_height + buffer:.2f}")

        # Only break if absolutely necessary (not enough space)
        if y - needed_height < self.layout.bottom_margin + buffer:
            logger.debug("*** PAGE BREAK REQUIRED ***")
                
            self.start_new_page()
            if redraw_function:
                redraw_function()  # Redraw headers/backgrounds on new page
                
            new_y = self.layout.page_size[1] - self.layout.banner_height - self.layout.top_margin
            
            logger.debug(f"New page started. New y position: {new_y:.2f}")
                
            return new_y
        
        logger.debug("No page break needed")
            
        return y

    def start_new_page(self, set_page_number: int = None) -> None:
        """Start a new page on the canvas."""
        self.canvas.showPage()
        # Increment the current page counter
        if set_page_number:
            self.current_page = set_page_number
        else:
            self.current_page += 1
        logger.debug(f"Started new page: {self.current_page}")
        # Reset colors (showPage resets graphics state)
        self.reset_graphics_state()
        
    def reset_graphics_state(self) -> None:
        """Reset the graphic state after a page break."""
        # Reset fill color to default text color
        if hasattr(self, 'theme') and self.theme:
            self.canvas.setFillColor(self.theme.get_color(self.theme.text_color))
            # Reset font to default
            self.canvas.setFont(self.theme.body_font, self.theme.body_font_size)
        logger.debug("Graphics state reset after page break")