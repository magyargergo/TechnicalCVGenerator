#!/usr/bin/env python
"""
Modern Template - Enhanced and fixed contemporary CV layout with sidebar and main content.
"""
import os
from typing import Dict, Any, Optional, List, Tuple, Callable

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors
from reportlab.lib.units import inch, mm
from reportlab.pdfbase.pdfmetrics import stringWidth

from cv_data import CVData
from theme import Theme
from layout import Layout
from templates.base_template import BaseTemplate
from text_utils import TextProcessor, CanvasHelper


class ModernTemplate(BaseTemplate):
    """
    Modern CV template with sidebar and main content.
    Enhanced with fixed text overflow, coloring, and improved layout management.
    """

    def render(self, canvas: Canvas, cv_data: CVData, theme: Theme, layout: Layout,
               profile_picture_path: Optional[str] = None) -> None:
        """
        Render the CV to the canvas with improved layout.

        Args:
            canvas: ReportLab canvas to draw on
            cv_data: CV data object
            theme: Theme object
            layout: Layout object
            profile_picture_path: Optional path to profile picture
        """
        # Initialize the base class
        super().render(canvas, cv_data, theme, layout, profile_picture_path)

        # Draw the modern layout with sidebar
        self.draw_modern_layout()

        # Set up column dimensions
        page_width, page_height = self.layout.page_size

        # Sidebar setup (left 1/3 of page)
        sidebar_width = page_width * 0.33
        sidebar_x = 0
        sidebar_start_y = page_height - self.layout.top_margin

        # Main content setup (right 2/3 of page)
        main_x = sidebar_width + 0.3 * inch
        main_width = page_width - main_x - self.layout.right_margin
        main_start_y = page_height - self.layout.top_margin

        # Generate the layout with improved content distribution
        self.generate_layout(
            sidebar_x, sidebar_width, sidebar_start_y,
            main_x, main_width, main_start_y
        )

    def draw_modern_layout(self) -> None:
        """Draw the base modern layout with sidebar."""
        page_width, page_height = self.layout.page_size
        sidebar_width = page_width * 0.33

        # Draw sidebar background with primary color
        self.canvas.setFillColor(self.theme.get_color(self.theme.primary_color))
        self.canvas.rect(
            0,
            0,
            sidebar_width,
            page_height,
            fill=1,
            stroke=0
        )

    def generate_layout(
            self,
            sidebar_x: float,
            sidebar_width: float,
            sidebar_y: float,
            main_x: float,
            main_width: float,
            main_y: float
    ) -> None:
        """
        Generate the sidebar and main content areas with improved layout planning.

        Args:
            sidebar_x: X-coordinate of sidebar
            sidebar_width: Width of sidebar
            sidebar_y: Starting Y-coordinate of sidebar
            main_x: X-coordinate of main content
            main_width: Width of main content
            main_y: Starting Y-coordinate of main content
        """

        # Function to redraw the sidebar on a new page
        def redraw_sidebar():
            self.draw_modern_layout()

        # Sidebar sections
        if self.profile_picture_path and os.path.exists(self.profile_picture_path):
            sidebar_y = self.add_profile_picture_section(sidebar_x, sidebar_width, sidebar_y)

        sidebar_y = self.add_contact_section(sidebar_x, sidebar_width, sidebar_y)
        sidebar_y = self.add_technical_skills_section(sidebar_x, sidebar_width, sidebar_y)
        sidebar_y = self.add_education_section(sidebar_x, sidebar_width, sidebar_y)
        sidebar_y = self.add_additional_info_section(sidebar_x, sidebar_width, sidebar_y)

        # Main content sections
        main_y = self.add_name_section(main_x, main_width, main_y)
        main_y = self.add_profile_section(main_x, main_width, main_y)
        main_y = self.add_experience_section(main_x, main_width, main_y)
        main_y = self.add_projects_section(main_x, main_width, main_y)

    def add_profile_picture_section(self, x: float, width: float, start_y: float) -> float:
        """Add profile picture to the sidebar with proper sizing."""
        if not self.profile_picture_path or not os.path.exists(self.profile_picture_path):
            return start_y

        # Center of sidebar
        center_x = x + width / 2
        circle_radius = min(width / 3, 1.2 * inch)
        circle_center_y = start_y - 1.5 * inch

        self.draw_profile_image(
            self.profile_picture_path,
            center_x,
            circle_center_y,
            circle_radius
        )

        return circle_center_y - circle_radius - 0.5 * inch

    def add_contact_section(self, x: float, width: float, start_y: float) -> float:
        """Add contact information to the sidebar with improved text handling."""
        candidate_data = self.cv_data.get_candidate_data()
        contact_details = candidate_data.get("contact", [])

        if not contact_details:
            return start_y

        y = self.draw_sidebar_section_header("CONTACT", x, start_y, width)
        y -= self.theme.line_spacing * 1.5

        # Draw each contact detail with proper wrapping
        for detail in contact_details:
            icon_code = detail.get("icon", "")
            text = detail.get("text", "")

            if icon_code and text:
                # Check for page break
                needed_height = self.theme.line_spacing * 1.5  # Approximate height for contact item
                y = self.check_page_break(y, needed_height, self.draw_modern_layout)

                y = self.draw_contact_item(icon_code, text, x, y, width)
                y -= self.theme.line_spacing * 1.2

        return y - self.theme.section_spacing

    def draw_contact_item(self, icon: str, text: str, x: float, y: float, width: float) -> float:
        """Draw a contact item with icon and proper text wrapping."""
        icon_font = "FontAwesome"
        icon_size = 12
        text_font = self.theme.body_font
        text_size = self.theme.body_font_size

        # Draw icon - ensure white color in sidebar
        self.canvas.setFont(icon_font, icon_size)
        self.canvas.setFillColor(colors.white)
        self.canvas.drawString(x + 0.3 * inch, y, icon)

        # Calculate available width for text
        text_x = x + 0.3 * inch + 0.4 * inch  # Icon indent + spacing
        available_width = width - 0.7 * inch

        # Process text - truncate if needed
        processor = TextProcessor(text_font, text_size)
        if self.canvas.stringWidth(text, text_font, text_size) > available_width:
            text = processor.truncate_with_ellipsis(text, available_width)

        # Draw text
        self.canvas.setFont(text_font, text_size)
        # Keep using white color for sidebar text
        self.canvas.setFillColor(colors.white)
        self.canvas.drawString(text_x, y, text)

        return y

    def add_technical_skills_section(self, x: float, width: float, start_y: float) -> float:
        """Add technical skills to the sidebar with better spacing and wrapping."""
        if not self.cv_data.has_section("technical_skills"):
            return start_y

        skills_data = self.cv_data.get_technical_skills()
        if not skills_data:
            return start_y

        # Fix: Use shorter title or adjust width to prevent overflow
        section_title = "TECHNICAL SKILLS"
        # Check if title fits in the sidebar width
        self.canvas.setFont(self.theme.header_font, self.theme.header_font_size)
        title_width = self.canvas.stringWidth(section_title, self.theme.header_font, self.theme.header_font_size)

        if title_width > width - 0.6 * inch:
            # If title is too long, use shorter version
            section_title = "TECH SKILLS"

        y = self.draw_sidebar_section_header(section_title, x, start_y, width)
        y -= self.theme.line_spacing * 1.5

        for category, skills in skills_data.items():
            # Check for page break before adding category
            needed_height = self.theme.line_spacing * 1.5  # Category heading
            skills_height = sum(self.calculate_text_height(skill, width - 0.6 * inch)
                                for skill in skills) + (len(skills) * self.theme.line_spacing * 0.7)
            total_height = needed_height + skills_height
            y = self.check_page_break(y, total_height, self.draw_modern_layout)

            # Category heading - ensure white color
            self.canvas.setFont(self.theme.header_font, self.theme.body_font_size)
            self.canvas.setFillColor(colors.white)
            self.canvas.drawString(x + 0.3 * inch, y, category)
            y -= self.theme.line_spacing * 1.2

            # Draw skills with proper wrapping
            for skill in skills:
                y = self.draw_sidebar_bullet_item(skill, x, y, width)
                y -= self.theme.line_spacing * 0.7

            y -= self.theme.line_spacing * 0.5

        return y - self.theme.section_spacing

    def draw_sidebar_bullet_item(self, text: str, x: float, y: float, width: float) -> float:
        """Draw a bulleted item in the sidebar with proper text wrapping."""
        bullet = "•"
        bullet_x = x + 0.4 * inch
        text_x = bullet_x + 0.2 * inch

        # Reduce available width to ensure text doesn't overflow
        available_width = width - (text_x - x) - 0.3 * inch

        # Draw bullet with white color
        self.canvas.setFont(self.theme.body_font, self.theme.body_font_size)
        self.canvas.setFillColor(colors.white)
        self.canvas.drawString(bullet_x, y, bullet)

        # Check if text needs to be wrapped
        processor = TextProcessor(self.theme.body_font, self.theme.body_font_size)
        text_width = self.canvas.stringWidth(text, self.theme.body_font, self.theme.body_font_size)

        if text_width > available_width:
            # Wrap the text over multiple lines
            lines = processor.wrap_text(text, available_width, hyphenate=True)

            # Draw each line
            for i, line in enumerate(lines):
                if i > 0:
                    y -= self.theme.line_spacing
                self.canvas.drawString(text_x, y, line)

            return y
        else:
            # Draw single line of text
            self.canvas.drawString(text_x, y, text)
            return y

    def add_education_section(self, x: float, width: float, start_y: float) -> float:
        """Add education section to the sidebar with better spacing and page breaks."""
        education_data = self.cv_data.get_education_data()
        if not education_data or not education_data.get("items"):
            return start_y

        y = self.draw_sidebar_section_header("EDUCATION", x, start_y, width)
        y -= self.theme.line_spacing * 1.5

        for edu in education_data.get("items", []):
            # Calculate height needed for this education item
            institution = edu.get("institution", "")
            degree = edu.get("degree", "")
            duration = edu.get("duration", "")

            needed_height = self.theme.line_spacing * 0.5  # Initial spacing

            # Institution text height
            institution_height = self.calculate_text_height(
                institution,
                width - 0.4 * inch,
                self.theme.header_font,
                self.theme.body_font_size
            )
            needed_height += institution_height + self.theme.line_spacing * 0.5

            # Degree and duration heights
            if degree:
                degree_height = self.calculate_text_height(
                    degree,
                    width - 0.5 * inch,
                    self.theme.body_font,
                    self.theme.body_font_size
                )
                needed_height += degree_height + self.theme.line_spacing * 0.5

            if duration:
                duration_height = self.calculate_text_height(
                    duration,
                    width - 0.5 * inch,
                    self.theme.body_font,
                    self.theme.body_font_size - 0.5
                )
                needed_height += duration_height

            needed_height += self.theme.paragraph_spacing

            # Check for page break
            y = self.check_page_break(y, needed_height, self.draw_modern_layout)

            # Institution name - ensure white color
            self.canvas.setFont(self.theme.header_font, self.theme.body_font_size)
            self.canvas.setFillColor(colors.white)

            # Use text wrapping for institution name if needed
            processor = TextProcessor(self.theme.header_font, self.theme.body_font_size)
            institution_width = self.canvas.stringWidth(institution, self.theme.header_font, self.theme.body_font_size)

            if institution_width > width - 0.4 * inch:
                # Wrap the text
                lines = processor.wrap_text(institution, width - 0.4 * inch, hyphenate=True)
                for i, line in enumerate(lines):
                    if i > 0:
                        y -= self.theme.line_spacing
                    self.canvas.drawString(x + 0.3 * inch, y, line)
            else:
                # Draw single line
                self.canvas.drawString(x + 0.3 * inch, y, institution)

            y -= self.theme.line_spacing * 0.5

            # Degree with white color
            if degree:
                self.canvas.setFont(self.theme.body_font, self.theme.body_font_size)
                self.canvas.setFillColor(colors.white)
                # Use text wrapping for degree if needed
                y = self.draw_wrapped_text(
                    text=degree,
                    x=x,
                    y=y,
                    max_width=width - 0.4 * inch,
                    indent=0.4 * inch,
                    hyphenate=True,
                    font_name=self.theme.body_font,
                    font_size=self.theme.body_font_size,
                    color="white"
                )
                y -= self.theme.line_spacing * 0.5

            # Duration with white color
            if duration:
                self.canvas.setFont(self.theme.body_font, self.theme.body_font_size - 0.5)
                self.canvas.setFillColor(colors.white)
                self.canvas.drawString(x + 0.4 * inch, y, duration)
                y -= self.theme.line_spacing

            y -= self.theme.paragraph_spacing

        return y - self.theme.section_spacing

    def add_additional_info_section(self, x: float, width: float, start_y: float) -> float:
        """Add additional information section to the sidebar with better text handling."""
        additional_info = self.cv_data.get_additional_info()
        if not additional_info:
            return start_y

        # Use shorter title to prevent overflow
        y = self.draw_sidebar_section_header("MORE DETAILS", x, start_y, width)
        y -= self.theme.line_spacing * 1.5

        for info in additional_info:
            # Check for page break
            needed_height = self.calculate_bulleted_text_height(info, width - 0.6 * inch)
            y = self.check_page_break(y, needed_height, self.draw_modern_layout)

            y = self.draw_sidebar_bullet_item(info, x, y, width)
            y -= self.theme.line_spacing

        return y - self.theme.section_spacing

    def draw_sidebar_section_header(self, title: str, x: float, y: float, width: float) -> float:
        """Draw a section header in the sidebar with consistent styling."""
        # Draw section title with white color
        self.canvas.setFont(self.theme.header_font, self.theme.header_font_size)
        self.canvas.setFillColor(colors.white)
        self.canvas.drawString(x + 0.3 * inch, y, title)

        # Draw underline with secondary color
        line_y = y - 0.15 * inch
        line_x_start = x + 0.3 * inch
        line_x_end = x + width - 0.3 * inch

        self.canvas.setLineWidth(1)
        self.canvas.setStrokeColor(self.theme.get_color(self.theme.secondary_color))
        self.canvas.line(line_x_start, line_y, line_x_end, line_y)

        return y

    def add_name_section(self, x: float, width: float, start_y: float) -> float:
        """Add candidate name as a large header in the main content area."""
        candidate_data = self.cv_data.get_candidate_data()
        name = candidate_data.get("name", "")

        if not name:
            return start_y

        # Draw name as a large header with primary color
        self.canvas.setFont(self.theme.header_font, 24)
        self.canvas.setFillColor(self.theme.get_color(self.theme.primary_color))
        self.canvas.drawString(x, start_y - 0.5 * inch, name)

        # Subtitle/job title if available with text color
        if "title" in candidate_data:
            self.canvas.setFont(self.theme.body_font, 14)
            self.canvas.setFillColor(self.theme.get_color(self.theme.text_color))
            self.canvas.drawString(x, start_y - 0.8 * inch, candidate_data["title"])
            return start_y - 1.2 * inch

        return start_y - 1 * inch

    def add_profile_section(self, x: float, width: float, start_y: float) -> float:
        """Add profile section to the main content area with better text handling."""
        profile_text = self.cv_data.get_profile_data()
        if not profile_text:
            return start_y

        y = self.draw_main_section_header("PROFILE", x, start_y, width)
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
            y = self.check_page_break(y, paragraph_height, self.draw_modern_layout)

            # Draw paragraph with text color
            y = self.draw_wrapped_text(
                text=paragraph,
                x=x,
                y=y,
                max_width=width,
                line_height=self.theme.line_spacing * 1.3,
                indent=0,
                hyphenate=True,
                color=self.theme.text_color
            )
            y -= self.theme.line_spacing

        return y - self.theme.section_spacing

    def add_experience_section(self, x: float, width: float, start_y: float) -> float:
        """Add experience section to the main content area with better color handling."""
        experience_data = self.cv_data.get_experience_data()
        if not experience_data or not experience_data.get("companies"):
            return start_y

        y = self.draw_main_section_header("PROFESSIONAL EXPERIENCE", x, start_y, width)
        y -= self.theme.line_spacing * 1.5

        companies = experience_data.get("companies", [])
        for company in companies:
            # Better height estimation and page break handling
            needed_height = self._estimate_company_height(company, width) + 20  # Add extra buffer
            y = self.check_page_break(y, needed_height, self.draw_modern_layout)

            # If we started a new page, redraw the modern layout
            if y == self.layout.page_size[1] - self.layout.top_margin:
                # Redraw section header
                y = self.draw_main_section_header("PROFESSIONAL EXPERIENCE", x, y, width)
                y -= self.theme.line_spacing * 1.5

            # Company name with primary color
            company_name = company.get("name", "")
            duration = company.get("totalDuration", "")

            # Draw company name with proper coloring
            self.canvas.setFont(self.theme.header_font, self.theme.body_font_size + 1)
            self.canvas.setFillColor(self.theme.get_color(self.theme.primary_color))
            self.canvas.drawString(x, y, company_name)

            # Company name width
            company_name_width = self.canvas.stringWidth(company_name, self.theme.header_font,
                                                         self.theme.body_font_size + 1)

            # Duration with text color - aligned to right if fits
            self.canvas.setFont(self.theme.body_font, self.theme.body_font_size)
            self.canvas.setFillColor(self.theme.get_color(self.theme.text_color))
            duration_width = self.canvas.stringWidth(duration, self.theme.body_font, self.theme.body_font_size)

            # Check if duration fits on same line
            if x + company_name_width + 20 + duration_width <= x + width:
                self.canvas.drawString(x + width - duration_width, y, duration)
                y -= self.theme.line_spacing * 1.2
            else:
                # Not enough space, put duration on next line
                y -= self.theme.line_spacing
                self.canvas.drawString(x + 20, y, duration)
                y -= self.theme.line_spacing * 0.7

            # Roles with proper coloring
            for role in company.get("roles", []):
                role_title = role.get("title", "")

                # Check for page break before role
                role_height = self.calculate_text_height(role_title, width - 0.2 * inch)
                responsibilities = role.get("responsibilities", [])
                resp_height = sum(self.calculate_bulleted_text_height(resp, width - 0.5 * inch)
                                  for resp in responsibilities) + (
                                          len(responsibilities) * self.theme.line_spacing * 0.5)
                total_role_height = role_height + resp_height + self.theme.line_spacing

                y = self.check_page_break(y, total_role_height, self.draw_modern_layout)

                # Role title with secondary color
                self.canvas.setFont(self.theme.header_font, self.theme.body_font_size)
                self.canvas.setFillColor(self.theme.get_color(self.theme.secondary_color))
                self.canvas.drawString(x + 0.2 * inch, y, role_title)

                y -= self.theme.line_spacing

                # Responsibilities with text color
                for resp in responsibilities:
                    y = self.draw_bulleted_text(
                        bullet="•",
                        text=resp,
                        x=x + 0.4 * inch,
                        y=y,
                        max_width=width - 0.5 * inch,
                        hyphenate=True,
                        text_color=self.theme.text_color
                    )
                    y -= self.theme.line_spacing * 0.5

                y -= self.theme.line_spacing

            y -= self.theme.paragraph_spacing

        return y - self.theme.section_spacing

    def _estimate_company_height(self, company: Dict[str, Any], width: float) -> float:
        """Estimate the height needed for a company entry to check page breaks."""
        line_height = self.theme.line_spacing

        # Company name and duration
        company_name = company.get("name", "")
        duration = company.get("totalDuration", "")

        # Calculate width and check if they fit on same line
        company_name_width = self.canvas.stringWidth(
            company_name, self.theme.header_font, self.theme.body_font_size + 1
        )
        duration_width = self.canvas.stringWidth(
            duration, self.theme.body_font, self.theme.body_font_size
        )

        if company_name_width + 20 + duration_width > width:
            # Need extra line for duration
            company_header_height = line_height * 2.5
        else:
            company_header_height = line_height * 1.5

        total_height = company_header_height

        for role in company.get("roles", []):
            role_title = role.get("title", "")
            role_title_height = line_height * 1.5

            # Responsibilities
            responsibilities = role.get("responsibilities", [])
            responsibilities_height = 0

            for resp in responsibilities:
                resp_height = self.calculate_bulleted_text_height(resp, width - 0.5 * inch)
                responsibilities_height += resp_height + line_height * 0.5

            total_height += role_title_height + responsibilities_height + line_height

        total_height += self.theme.paragraph_spacing * 2

        return total_height

    def add_projects_section(self, x: float, width: float, start_y: float) -> float:
        """Add projects section to the main content area with better color handling."""
        projects = self.cv_data.get_projects_data()
        if not projects:
            return start_y

        y = self.draw_main_section_header("PROJECTS & ACHIEVEMENTS", x, start_y, width)
        y -= self.theme.line_spacing * 1.5

        for project in projects:
            title = project.get("title", "")
            description = project.get("description", "")

            # Calculate needed height for this project
            title_height = self.calculate_text_height(title, width, self.theme.header_font, self.theme.body_font_size)
            desc_height = 0
            if description:
                desc_height = self.calculate_text_height(description, width)

            project_height = title_height + desc_height + self.theme.line_spacing * 1.5

            # Check for page break
            y = self.check_page_break(y, project_height, self.draw_modern_layout)

            # Project title with primary color
            self.canvas.setFont(self.theme.header_font, self.theme.body_font_size)
            self.canvas.setFillColor(self.theme.get_color(self.theme.primary_color))
            self.canvas.drawString(x, y, title)

            y -= self.theme.line_spacing

            # Description with text color
            if description:
                y = self.draw_wrapped_text(
                    text=description,
                    x=x,
                    y=y,
                    max_width=width,
                    indent=0.2 * inch,
                    hyphenate=True,
                    color=self.theme.text_color
                )

            y -= self.theme.paragraph_spacing

        # References if available
        references = self.cv_data.get_references()
        if references:
            # Check for page break
            ref_height = self.calculate_text_height(references, width) + self.theme.line_spacing * 2
            y = self.check_page_break(y, ref_height, self.draw_modern_layout)

            y = self.draw_main_section_header("REFERENCES", x, y, width)
            y -= self.theme.line_spacing * 1.2

            y = self.draw_wrapped_text(
                text=references,
                x=x,
                y=y,
                max_width=width,
                indent=0,
                hyphenate=False,
                color=self.theme.text_color
            )

        return y

    def draw_main_section_header(self, title: str, x: float, y: float, width: float) -> float:
        """Draw a section header in the main content area with consistent styling."""
        # Draw section title with primary color
        self.canvas.setFont(self.theme.header_font, self.theme.header_font_size + 1)
        self.canvas.setFillColor(self.theme.get_color(self.theme.primary_color))
        self.canvas.drawString(x, y, title)

        # Draw decorative line with primary color
        line_y = y - 0.15 * inch
        self.canvas.setLineWidth(1)
        self.canvas.setStrokeColor(self.theme.get_color(self.theme.primary_color))
        self.canvas.line(x, line_y, x + width, line_y)

        return y

    def check_page_break(self, y: float, needed_height: float, redraw_function: Optional[Callable] = None) -> float:
        """
        Check if a page break is needed before drawing content.
        Enhanced with callback for redrawing the sidebar.

        Args:
            y: Current y position
            needed_height: Height needed for the content
            redraw_function: Function to call after page break to redraw sidebar

        Returns:
            New y position, possibly on a new page
        """
        # Add a buffer to avoid content too close to bottom
        buffer = 15

        if y - needed_height < self.layout.bottom_margin + buffer:
            self.start_new_page()
            if redraw_function:
                redraw_function()  # Redraw sidebar
            return self.layout.page_size[1] - self.layout.top_margin
        return y