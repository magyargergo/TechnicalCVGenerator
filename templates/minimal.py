#!/usr/bin/env python
"""
Minimal Template - Enhanced clean, minimalist CV layout with improved dynamic content handling.
"""
import os
from typing import Dict, Any, Optional, List, Tuple, Callable

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth

from cv_data import CVData
from theme import Theme
from layout import Layout
from templates.base_template import BaseTemplate
from text_utils import TextProcessor, CanvasHelper


class MinimalTemplate(BaseTemplate):
    """
    Enhanced minimal CV template with clean, modern design.
    Single column layout with improved spacing, overflow handling, and dynamic content.
    """

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
        # Initialize the base class
        super().render(canvas, cv_data, theme, layout, profile_picture_path)

        # Pre-calculate section heights for better layout planning
        self._pre_calculate_section_heights()

        # Draw the minimalist header
        self.draw_header()

        # Start content layout
        page_width, page_height = self.layout.page_size
        content_x = self.layout.left_margin
        content_width = page_width - self.layout.left_margin - self.layout.right_margin

        # Use a top margin plus a bit more for the header
        content_y = page_height - self.layout.top_margin - 1.5 * inch

        # Save for redrawing when needed
        self.content_x = content_x
        self.content_width = content_width

        # Generate sections in sequence with improved spacing
        self.generate_content_layout(content_x, content_width, content_y)

    def _pre_calculate_section_heights(self) -> None:
        """
        Pre-calculate heights of various sections to plan layout better.
        """
        page_width, page_height = self.layout.page_size
        content_width = page_width - self.layout.left_margin - self.layout.right_margin

        self.section_heights = {}

        # Header height (fixed)
        self.section_heights["header"] = 1.5 * inch

        # Profile section height
        if self.cv_data.has_section("profile"):
            profile_text = self.cv_data.get_profile_data()
            profile_height = self.theme.line_spacing * 2  # Header

            paragraphs = profile_text.split('\n\n')
            for paragraph in paragraphs:
                paragraph_height = CanvasHelper.estimate_text_block_height(
                    paragraph,
                    content_width,
                    self.theme.body_font,
                    self.theme.body_font_size,
                    self.theme.line_spacing * 1.3,
                    True
                )
                profile_height += paragraph_height + self.theme.line_spacing

            self.section_heights["profile"] = profile_height + self.theme.section_spacing
        else:
            self.section_heights["profile"] = 0

        # Skills section height
        if self.cv_data.has_section("technical_skills"):
            skills_data = self.cv_data.get_technical_skills()
            skills_height = self.theme.line_spacing * 2  # Header

            for category, skills in skills_data.items():
                category_width = stringWidth(category + ":", self.theme.header_font, self.theme.body_font_size)

                if category_width < content_width * 0.25 and len(", ".join(skills)) < 50:
                    # Single line
                    skills_height += self.theme.line_spacing * 1.2
                else:
                    # Category heading plus wrapped skills
                    skills_height += self.theme.line_spacing
                    skills_text = ", ".join(skills)
                    skills_text_height = CanvasHelper.estimate_text_block_height(
                        skills_text,
                        content_width - 5,
                        self.theme.body_font,
                        self.theme.body_font_size,
                        self.theme.line_spacing,
                        False
                    )
                    skills_height += skills_text_height + self.theme.line_spacing * 1.2

            self.section_heights["skills"] = skills_height + self.theme.section_spacing
        else:
            self.section_heights["skills"] = 0

        # Experience section height
        if self.cv_data.has_section("experience"):
            experience_data = self.cv_data.get_experience_data()
            companies = experience_data.get("companies", [])

            experience_height = self.theme.line_spacing * 2  # Header

            for company in companies:
                company_height = self._estimate_company_height(company, content_width)
                experience_height += company_height

            self.section_heights["experience"] = experience_height + self.theme.section_spacing
        else:
            self.section_heights["experience"] = 0

        # Education section height
        if self.cv_data.has_section("education"):
            education_data = self.cv_data.get_education_data()
            education_height = self.theme.line_spacing * 2  # Header

            for edu in education_data.get("items", []):
                institution = edu.get("institution", "")
                degree = edu.get("degree", "")
                duration = edu.get("duration", "")

                # Institution and duration on same line
                education_height += self.theme.line_spacing

                # Degree on separate line if present
                if degree:
                    degree_height = CanvasHelper.estimate_text_block_height(
                        degree,
                        content_width - 10,
                        self.theme.body_font,
                        self.theme.body_font_size,
                        self.theme.line_spacing,
                        True
                    )
                    education_height += degree_height + self.theme.line_spacing

                education_height += self.theme.paragraph_spacing * 0.5

            self.section_heights["education"] = education_height + self.theme.section_spacing
        else:
            self.section_heights["education"] = 0

        # Projects section height
        if self.cv_data.has_section("projects"):
            projects = self.cv_data.get_projects_data()
            projects_height = self.theme.line_spacing * 2  # Header

            for project in projects:
                title = project.get("title", "")
                description = project.get("description", "")

                # Title
                projects_height += self.theme.line_spacing

                # Description
                if description:
                    desc_height = CanvasHelper.estimate_text_block_height(
                        description,
                        content_width - 10,
                        self.theme.body_font,
                        self.theme.body_font_size,
                        self.theme.line_spacing,
                        True
                    )
                    projects_height += desc_height + self.theme.line_spacing

                projects_height += self.theme.paragraph_spacing * 0.5

            self.section_heights["projects"] = projects_height + self.theme.section_spacing
        else:
            self.section_heights["projects"] = 0

        # Additional info section height
        if self.cv_data.has_section("additional_info"):
            additional_info = self.cv_data.get_additional_info()
            additional_info_height = self.theme.line_spacing * 2  # Header

            for info in additional_info:
                info_height = CanvasHelper.estimate_bulleted_text_height(
                    info,
                    content_width - 5,
                    5,
                    self.theme.body_font,
                    self.theme.body_font_size,
                    self.theme.line_spacing,
                    True
                )
                additional_info_height += info_height + self.theme.line_spacing * 0.6

            self.section_heights["additional_info"] = additional_info_height + self.theme.section_spacing
        else:
            self.section_heights["additional_info"] = 0

    def draw_header(self) -> None:
        """Draw the minimalist header with name and contact info."""
        page_width, page_height = self.layout.page_size

        # Get candidate data
        candidate_data = self.cv_data.get_candidate_data()
        name = candidate_data.get("name", "")
        contact_details = candidate_data.get("contact", [])

        # Draw name with proper styling
        self.canvas.setFont(self.theme.header_font, 18)
        self.set_fill_color(self.theme.primary_color)
        name_y = page_height - self.layout.top_margin - 0.3 * inch

        # Calculate name width and center if needed
        name_width = self.canvas.stringWidth(name, self.theme.header_font, 18)
        name_x = self.layout.left_margin

        self.canvas.drawString(name_x, name_y, name)

        # Draw line under name
        line_y = name_y - 0.2 * inch
        self.canvas.setLineWidth(1)
        self.set_stroke_color(self.theme.accent_color)
        self.canvas.line(
            self.layout.left_margin,
            line_y,
            page_width - self.layout.right_margin,
            line_y
        )

        # Draw contact details in a horizontal row with improved layout
        contact_y = line_y - 0.3 * inch
        self.draw_contact_details_horizontal(contact_details, contact_y)

        # Draw profile picture if available
        if self.profile_picture_path and os.path.exists(self.profile_picture_path):
            circle_radius = min(30, self.layout.right_margin * 0.8)  # Limit size based on margin
            circle_center_x = page_width - self.layout.right_margin - circle_radius
            circle_center_y = name_y - 0.1 * inch
            self.draw_profile_image(
                self.profile_picture_path,
                circle_center_x,
                circle_center_y,
                circle_radius
            )

    def draw_contact_details_horizontal(self, contact_details: List[Dict[str, str]], y: float) -> None:
        """Draw contact details in a horizontal row with improved spacing and truncation."""
        page_width = self.layout.page_size[0]
        icon_font = "FontAwesome"
        icon_font_size = 9
        text_font = self.theme.body_font
        text_font_size = 9
        spacing = 25  # Increased spacing between items

        # Limit to the most important items to avoid overflow
        max_items = min(4, len(contact_details))
        filtered_contacts = contact_details[:max_items]

        # Calculate total width needed
        total_width = 0
        items_width = []

        # Process each contact detail - truncate if needed
        processed_texts = []

        for detail in filtered_contacts:
            icon_code = detail["icon"]
            # Truncate text if too long (e.g., email addresses)
            text = detail["text"]
            processor = TextProcessor(text_font, text_font_size)

            # Maximum width for a single contact item
            max_item_width = (page_width - self.layout.left_margin - self.layout.right_margin) / max_items - spacing

            # Calculate current width
            self.canvas.setFont(icon_font, icon_font_size)
            icon_width = self.canvas.stringWidth(icon_code, icon_font, icon_font_size)

            self.canvas.setFont(text_font, text_font_size)
            text_width = self.canvas.stringWidth(text, text_font, text_font_size)

            # Truncate if needed
            if icon_width + 5 + text_width > max_item_width:
                text = processor.truncate_with_ellipsis(text, max_item_width - icon_width - 5)
                text_width = self.canvas.stringWidth(text, text_font, text_font_size)

            processed_texts.append(text)
            item_width = icon_width + 5 + text_width
            items_width.append(item_width)
            total_width += item_width

        # Add spacing between items
        total_width += spacing * (len(filtered_contacts) - 1)

        # Calculate starting position to center the contact details
        start_x = (page_width - total_width) / 2
        if start_x < self.layout.left_margin:
            start_x = self.layout.left_margin  # Ensure minimum margin

        # Draw each contact detail
        current_x = start_x
        self.set_fill_color(self.theme.text_color)

        for i, detail in enumerate(filtered_contacts):
            icon_code = detail["icon"]
            text = processed_texts[i]

            # Draw icon
            self.canvas.setFont(icon_font, icon_font_size)
            self.canvas.drawString(current_x, y, icon_code)
            icon_width = self.canvas.stringWidth(icon_code, icon_font, icon_font_size)

            # Draw text
            self.canvas.setFont(text_font, text_font_size)
            self.canvas.drawString(current_x + icon_width + 5, y, text)

            # Move to next item
            current_x += items_width[i] + spacing

            # Ensure we don't overflow
            if current_x + items_width[i] > page_width - self.layout.right_margin:
                break

    def generate_content_layout(self, x: float, width: float, start_y: float) -> None:
        """
        Generate content sections in sequence with improved layout planning.

        Args:
            x: X-coordinate to start content
            width: Width available for content
            start_y: Starting Y-coordinate
        """
        # Init current y position
        y = start_y

        # Calculate total content height
        total_content_height = sum([
            self.section_heights.get("profile", 0),
            self.section_heights.get("skills", 0),
            self.section_heights.get("experience", 0),
            self.section_heights.get("education", 0),
            self.section_heights.get("projects", 0),
            self.section_heights.get("additional_info", 0)
        ])

        # Calculate available height on first page
        available_first_page = y - self.layout.bottom_margin

        # Create a callback for redrawing header after page breaks
        def redraw_header():
            self.draw_header()

        # Profile first - often showcases key information
        if self.cv_data.has_section("profile"):
            y = self.add_profile_section(x, width, y)

        # Skills next - typically compact and important
        if self.cv_data.has_section("technical_skills"):
            y = self.add_skills_section(x, width, y)

        # Experience - usually the largest and most important section
        if self.cv_data.has_section("experience"):
            y = self.add_experience_section(x, width, y)

        # Education
        if self.cv_data.has_section("education"):
            # Check if enough space remains on current page
            if y - self.section_heights.get("education", 0) < self.layout.bottom_margin:
                # Start new page
                self.start_new_page()
                redraw_header()
                y = self.layout.page_size[1] - self.layout.top_margin - 1.5 * inch

            y = self.add_education_section(x, width, y)

        # Projects
        if self.cv_data.has_section("projects"):
            # Check if enough space remains on current page
            if y - self.section_heights.get("projects", 0) < self.layout.bottom_margin:
                # Start new page
                self.start_new_page()
                redraw_header()
                y = self.layout.page_size[1] - self.layout.top_margin - 1.5 * inch

            y = self.add_projects_section(x, width, y)

        # Additional info - typically shorter and less critical
        if self.cv_data.has_section("additional_info"):
            # Check if enough space remains on current page
            if y - self.section_heights.get("additional_info", 0) < self.layout.bottom_margin:
                # Start new page
                self.start_new_page()
                redraw_header()
                y = self.layout.page_size[1] - self.layout.top_margin - 1.5 * inch

            y = self.add_additional_info_section(x, width, y)

    def add_profile_section(self, x: float, width: float, start_y: float) -> float:
        """Add profile section with improved text handling."""
        profile_text = self.cv_data.get_profile_data()
        if not profile_text:
            return start_y

        y = self.draw_minimal_section_header("PROFILE", x, start_y, width)
        y -= self.theme.line_spacing

        # Split the profile text into paragraphs
        paragraphs = profile_text.split('\n\n')

        for paragraph in paragraphs:
            # Check for page break
            paragraph_height = self.calculate_text_height(
                paragraph,
                width,
                line_height=self.theme.line_spacing * 1.3
            )
            y = self.check_page_break(y, paragraph_height, self.draw_header)

            y = self.draw_wrapped_text(
                text=paragraph,
                x=x,
                y=y,
                max_width=width,
                line_height=self.theme.line_spacing * 1.3,
                hyphenate=True
            )
            y -= self.theme.line_spacing

        return y - self.theme.section_spacing

    def add_skills_section(self, x: float, width: float, start_y: float) -> float:
        """Add skills section with improved layout and optimal space usage."""
        skills_data = self.cv_data.get_technical_skills()
        if not skills_data:
            return start_y

        y = self.draw_minimal_section_header("TECHNICAL SKILLS", x, start_y, width)
        y -= self.theme.line_spacing * 1.2

        # Organize skills in a more compact layout
        for category, skills in skills_data.items():
            # Check for page break before adding category
            category_text = f"{category}: {', '.join(skills)}"
            needed_height = self.calculate_text_height(category_text, width)
            y = self.check_page_break(y, needed_height, self.draw_header)

            # Category heading
            self.canvas.setFont(self.theme.header_font, self.theme.body_font_size)
            self.set_fill_color(self.theme.text_color)
            self.canvas.drawString(x, y, category + ":")
            category_width = self.canvas.stringWidth(category + ":", self.theme.header_font, self.theme.body_font_size)

            # For very short categories, put skills on same line
            if category_width < width * 0.25 and len(", ".join(skills)) < 50:
                # Draw skills as a comma-separated list on same line
                skills_text = ", ".join(skills)
                self.canvas.setFont(self.theme.body_font, self.theme.body_font_size)
                self.canvas.drawString(x + category_width + 5, y, skills_text)
                y -= self.theme.line_spacing * 1.2
            else:
                # Draw skills on next line with proper wrapping
                y -= self.theme.line_spacing
                skills_text = ", ".join(skills)
                y = self.draw_wrapped_text(
                    text=skills_text,
                    x=x,
                    y=y,
                    max_width=width - 5,
                    indent=10,
                    hyphenate=False
                )
                y -= self.theme.line_spacing * 1.2

        return y - self.theme.section_spacing

    def add_experience_section(self, x: float, width: float, start_y: float) -> float:
        """Add experience section with better layout and overflow handling."""
        experience_data = self.cv_data.get_experience_data()
        if not experience_data or not experience_data.get("companies"):
            return start_y

        y = self.draw_minimal_section_header("PROFESSIONAL EXPERIENCE", x, start_y, width)
        y -= self.theme.line_spacing * 1.5

        companies = experience_data.get("companies", [])
        for company in companies:
            # Check if we need a page break
            needed_height = self._estimate_company_height(company, width)
            y = self.check_page_break(y, needed_height, self.draw_header)

            # If we started a new page, redraw the header
            if y == self.layout.page_size[1] - self.layout.top_margin - 1.5 * inch:
                # Redraw section header
                y = self.draw_minimal_section_header("PROFESSIONAL EXPERIENCE", x, y, width)
                y -= self.theme.line_spacing * 1.5

            # Company name and duration with better layout
            company_name = company.get("name", "")
            duration = company.get("totalDuration", "")

            self.canvas.setFont(self.theme.header_font, self.theme.body_font_size + 1)
            self.set_fill_color(self.theme.primary_color)

            # Check if company name is too long to allow duration on same line
            company_name_width = self.canvas.stringWidth(company_name, self.theme.header_font,
                                                         self.theme.body_font_size + 1)

            # Draw company name
            self.canvas.drawString(x, y, company_name)

            # Duration right-aligned if it fits, otherwise on next line
            self.canvas.setFont(self.theme.body_font, self.theme.body_font_size)
            self.set_fill_color(self.theme.text_color)
            duration_width = self.canvas.stringWidth(duration, self.theme.body_font, self.theme.body_font_size)

            if x + company_name_width + 20 + duration_width <= x + width:
                # Fits on same line
                self.canvas.drawString(x + width - duration_width, y, duration)
                y -= self.theme.line_spacing * 1.2
            else:
                # Put duration on next line
                y -= self.theme.line_spacing
                self.canvas.drawString(x + 10, y, duration)
                y -= self.theme.line_spacing * 0.7

            # Roles within the company
            for role in company.get("roles", []):
                role_title = role.get("title", "")

                # Calculate needed height for this role
                responsibilities = role.get("responsibilities", [])
                role_height = self.theme.line_spacing
                resp_height = sum(self.calculate_bulleted_text_height(resp, width - 20) +
                                  self.theme.line_spacing * 0.5 for resp in responsibilities)
                total_role_height = role_height + resp_height + self.theme.line_spacing * 0.5

                # Check for page break before adding role
                y = self.check_page_break(y, total_role_height, self.draw_header)

                self.canvas.setFont(self.theme.header_font, self.theme.body_font_size)
                self.set_fill_color(self.theme.secondary_color)  # Use secondary color for role title
                self.canvas.drawString(x + 10, y, role_title)

                y -= self.theme.line_spacing

                # Responsibilities with better spacing
                for resp in responsibilities:
                    y = self.draw_bulleted_text(
                        bullet="•",
                        text=resp,
                        x=x + 20,
                        y=y,
                        max_width=width - 20,
                        hyphenate=True
                    )
                    y -= self.theme.line_spacing * 0.5

                y -= self.theme.line_spacing * 0.5

            y -= self.theme.paragraph_spacing

        return y - self.theme.section_spacing

    def _estimate_company_height(self, company: Dict[str, Any], width: float) -> float:
        """Estimate height needed for a company section with better accuracy."""
        line_height = self.theme.line_spacing

        # Company name and duration
        company_name = company.get("name", "")
        duration = company.get("totalDuration", "")

        company_name_width = stringWidth(company_name, self.theme.header_font, self.theme.body_font_size + 1)
        duration_width = stringWidth(duration, self.theme.body_font, self.theme.body_font_size)

        # Check if duration fits on same line
        if company_name_width + 20 + duration_width <= width:
            company_header_height = line_height * 1.2
        else:
            company_header_height = line_height * 2  # Extra line for duration

        total_height = company_header_height

        for role in company.get("roles", []):
            # Role title
            role_title_height = line_height

            # Responsibilities
            responsibilities = role.get("responsibilities", [])
            responsibilities_height = 0

            for resp in responsibilities:
                resp_height = self.calculate_bulleted_text_height(resp, width - 20)
                responsibilities_height += resp_height + line_height * 0.5

            total_height += role_title_height + responsibilities_height + line_height

        # Add paragraph spacing
        total_height += self.theme.paragraph_spacing

        return total_height

    def add_education_section(self, x: float, width: float, start_y: float) -> float:
        """Add education section with better layout and spacing."""
        education_data = self.cv_data.get_education_data()
        if not education_data or not education_data.get("items"):
            return start_y

        y = self.draw_minimal_section_header("EDUCATION", x, start_y, width)
        y -= self.theme.line_spacing * 1.5

        for edu in education_data.get("items", []):
            institution = edu.get("institution", "")
            degree = edu.get("degree", "")
            duration = edu.get("duration", "")

            # Calculate needed height for this education item
            edu_height = self.theme.line_spacing  # Institution and duration
            if degree:
                degree_height = self.calculate_text_height(degree, width - 10)
                edu_height += degree_height + self.theme.line_spacing
            edu_height += self.theme.paragraph_spacing * 0.5

            # Check for page break
            y = self.check_page_break(y, edu_height, self.draw_header)

            # Institution name
            self.canvas.setFont(self.theme.header_font, self.theme.body_font_size)
            self.set_fill_color(self.theme.primary_color)
            self.canvas.drawString(x, y, institution)

            # Duration right-aligned
            self.canvas.setFont(self.theme.body_font, self.theme.body_font_size - 0.5)
            self.set_fill_color(self.theme.text_color)
            duration_width = self.canvas.stringWidth(duration, self.theme.body_font, self.theme.body_font_size - 0.5)

            # Ensure institution name doesn't overflow with duration
            institution_width = self.canvas.stringWidth(institution, self.theme.header_font, self.theme.body_font_size)
            if x + institution_width + 10 < x + width - duration_width:
                self.canvas.drawString(x + width - duration_width, y, duration)
            else:
                # Put duration on next line if no space
                y -= self.theme.line_spacing * 0.8
                self.canvas.drawString(x + 10, y, duration)
                y -= self.theme.line_spacing * 0.2

            y -= self.theme.line_spacing

            # Degree with proper wrapping
            if degree:
                y = self.draw_wrapped_text(
                    text=degree,
                    x=x + 10,
                    y=y,
                    max_width=width - 10,
                    hyphenate=True
                )
                y -= self.theme.line_spacing

            y -= self.theme.paragraph_spacing * 0.5

        return y - self.theme.section_spacing

    def add_projects_section(self, x: float, width: float, start_y: float) -> float:
        """Add projects section with better layout and overflow handling."""
        projects = self.cv_data.get_projects_data()
        if not projects:
            return start_y

        y = self.draw_minimal_section_header("PROJECTS & ACHIEVEMENTS", x, start_y, width)
        y -= self.theme.line_spacing * 1.5

        for project in projects:
            title = project.get("title", "")
            description = project.get("description", "")

            # Calculate needed height for this project
            project_height = self.theme.line_spacing  # Title
            if description:
                desc_height = self.calculate_text_height(description, width - 10)
                project_height += desc_height + self.theme.line_spacing
            project_height += self.theme.paragraph_spacing * 0.5

            # Check for page break
            y = self.check_page_break(y, project_height, self.draw_header)

            # Project title
            self.canvas.setFont(self.theme.header_font, self.theme.body_font_size)
            self.set_fill_color(self.theme.primary_color)
            y = self.draw_wrapped_text(
                text=title,
                x=x,
                y=y,
                max_width=width,
                font_name=self.theme.header_font,
                font_size=self.theme.body_font_size,
                color=self.theme.primary_color
            )

            y -= self.theme.line_spacing

            # Description with proper wrapping
            if description:
                y = self.draw_wrapped_text(
                    text=description,
                    x=x + 10,
                    y=y,
                    max_width=width - 10,
                    hyphenate=True
                )
                y -= self.theme.line_spacing

            y -= self.theme.paragraph_spacing * 0.5

        return y - self.theme.section_spacing

    def add_additional_info_section(self, x: float, width: float, start_y: float) -> float:
        """Add additional info section with better layout and spacing."""
        additional_info = self.cv_data.get_additional_info()
        if not additional_info:
            return start_y

        y = self.draw_minimal_section_header("ADDITIONAL INFORMATION", x, start_y, width)
        y -= self.theme.line_spacing * 1.5

        for info in additional_info:
            # Check for page break
            info_height = self.calculate_bulleted_text_height(info, width - 5)
            y = self.check_page_break(y, info_height + self.theme.line_spacing * 0.6, self.draw_header)

            y = self.draw_bulleted_text(
                bullet="•",
                text=info,
                x=x + 5,
                y=y,
                max_width=width - 5,
                hyphenate=True
            )
            y -= self.theme.line_spacing * 0.6

        return y - self.theme.section_spacing

    def draw_minimal_section_header(self, title: str, x: float, y: float, width: float) -> float:
        """Draw a minimal section header with only text and an underline."""
        # Draw section title
        self.canvas.setFont(self.theme.header_font, self.theme.header_font_size + 1)
        self.set_fill_color(self.theme.primary_color)
        self.canvas.drawString(x, y, title)

        # Draw underline
        line_y = y - 0.1 * inch
        self.canvas.setLineWidth(0.5)
        self.set_stroke_color(self.theme.accent_color)
        self.canvas.line(x, line_y, x + width * 0.4, line_y)

        return y

    def check_page_break(self, y: float, needed_height: float, redraw_function: Callable = None) -> float:
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
        if y - needed_height < self.layout.bottom_margin:
            self.start_new_page()
            if redraw_function:
                redraw_function()
            return self.layout.page_size[1] - self.layout.top_margin - 1.5 * inch
        return y