#!/usr/bin/env python
"""
CV Generator - Enhanced main class for CV generation.
This module provides an improved flexible CV generation system with better layout management.
"""
import os
import logging
from typing import Dict, Any, Optional, List, Tuple, Union
import json
import copy
from datetime import datetime

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.units import inch

from cv_data import CVData
from theme import Theme
from layout import Layout
from template_manager import TemplateManager
from font_manager import FontManager

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('cv_generator')


class CVGenerator:
    """
    Enhanced main class for generating CV PDFs with improved layout handling.
    Orchestrates the components of the CV system.
    """

    def __init__(self, debug_mode: bool = False):
        """
        Initialize the CV Generator with necessary components.

        Args:
            debug_mode: Enable debug mode for additional logging and debug information
        """
        self.template_manager = TemplateManager()
        self.font_manager = FontManager()
        self.register_default_templates()
        self.debug_mode = debug_mode

        if self.debug_mode:
            logger.setLevel(logging.DEBUG)
            logger.debug("CVGenerator initialized in debug mode")

    def register_default_templates(self):
        """Register the built-in templates with improved implementations."""
        # Import here to avoid circular imports
        try:
            from templates.two_column import TwoColumnTemplate
            from templates.modern import ModernTemplate
            from templates.minimal import MinimalTemplate

            self.template_manager.register_template("two_column", TwoColumnTemplate())
            self.template_manager.register_template("modern", ModernTemplate())
            self.template_manager.register_template("minimal", MinimalTemplate())

            logger.debug(f"Registered templates: {self.template_manager.list_templates()}")
        except ImportError as e:
            logger.error(f"Error importing templates: {e}")
            raise

    def create_cv(
            self,
            data_path: str,
            output_path: str,
            template_name: str,
            profile_picture_path: Optional[str] = None
    ) -> None:
        """
        Create a CV using the specified template and data.

        Args:
            data_path: Path to the JSON file containing CV data
            output_path: Path to save the generated CV
            template_name: Name of the template to use
            profile_picture_path: Optional path to a profile picture
        """
        # Load and prepare CV data
        cv_data = CVData(self.debug_mode)
        try:
            cv_data.load(data_path, debug_mode=self.debug_mode)
            cv_data.validate()
            logger.debug("CV data loaded and validated successfully")
        except Exception as e:
            logger.error(f"Error loading CV data: {e}")
            raise

        # Create a copy for optimization
        optimized_data = self._optimize_cv_content(cv_data)

        # Adjust spacing based on content density
        content_density = self._calculate_content_density(optimized_data)
        logger.debug(f"Calculated content density: {content_density:.2f}")
        theme = self._adjust_theme_for_content_density(content_density)

        # Create output directory if it doesn't exist. When output_path
        # is just a filename without any directory component, os.path.dirname
        # returns an empty string which would cause ``os.makedirs`` to raise
        # ``FileNotFoundError``.  Guard against this by checking the directory
        # portion before attempting to create it.
        output_dir = os.path.dirname(os.path.abspath(output_path))
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Get layout data from CVData (which includes defaults and user overrides from JSON)
        layout_data_dict = optimized_data.get_layout_data() 
        # Create layout object using Layout.from_dict
        layout = Layout.from_dict(layout_data_dict)
        
        # Debug margins
        logger.info(f"Using layout margins: left={layout.left_margin/inch:.2f}in, right={layout.right_margin/inch:.2f}in, top={layout.top_margin/inch:.2f}in, bottom={layout.bottom_margin/inch:.2f}in")

        # Ensure all required fonts are available BEFORE creating the canvas
        font_manager = FontManager(debug_mode=self.debug_mode)
        try:
            font_manager.ensure_fonts_available()
            logger.debug(f"Fonts registered successfully: {font_manager.fonts_registered}")
        except Exception as e:
            logger.error(f"Error registering fonts: {e}")
            # Continue with default fonts if custom ones fail

        # Verify that the theme's fonts are actually available from the font manager
        # Update theme to use available fonts if needed
        if theme.header_font not in font_manager.fonts_registered:
            logger.warning(f"Header font {theme.header_font} not available, using fallback")
            theme.header_font = "Helvetica-Bold"
            
        if theme.body_font not in font_manager.fonts_registered:
            logger.warning(f"Body font {theme.body_font} not available, using fallback")
            theme.body_font = "Helvetica"
            
        # Initialize ReportLab canvas with better Word compatibility
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfgen.canvas import Canvas

        # Create canvas with improved Word editability
        page_size = layout.page_size
        pdf_canvas = Canvas(output_path, pagesize=page_size)
        
        # Set PDF document properties
        pdf_canvas.setTitle(f"{cv_data.get_candidate_data().get('name', 'CV')} - Curriculum Vitae")
        pdf_canvas.setAuthor(cv_data.get_candidate_data().get('name', 'CV Generator User'))
        pdf_canvas.setSubject("Curriculum Vitae")
        pdf_canvas.setKeywords("CV, resume, curriculum vitae")
        
        # Make PDF more Word-friendly by setting lower compression
        pdf_canvas.setPageCompression(0)  # Disable compression for better editability
        
        # Ensure default font is set on the canvas
        pdf_canvas.setFont(theme.body_font, theme.body_font_size)
        
        logger.debug(f"Canvas initialized with page size: {page_size}, default font: {theme.body_font}")

        # Render the CV
        logger.info(f"Rendering CV with template '{template_name}'")
        template = self._get_template_by_name(template_name)
        try:
            template.render(pdf_canvas, optimized_data, theme, layout, profile_picture_path)
        except Exception as e:
            logger.error(f"Error rendering CV: {e}")
            raise

        # Save the PDF
        pdf_canvas.save()
        logger.info(f"CV created successfully: {output_path}")

    def _validate_input_files(self, data_path: str, profile_picture_path: Optional[str] = None) -> None:
        """
        Validate input files.

        Args:
            data_path: Path to CV data JSON
            profile_picture_path: Optional path to profile picture

        Raises:
            FileNotFoundError: If files don't exist
        """
        if not os.path.exists(data_path):
            logger.error(f"CV data file not found: {data_path}")
            raise FileNotFoundError(f"CV data file not found: {data_path}")

        if profile_picture_path and not os.path.exists(profile_picture_path):
            logger.warning(f"Profile picture not found: {profile_picture_path}")
            # Don't raise an error, just log a warning

    def _create_theme_layout(
            self,
            cv_data: CVData,
            theme_override: Optional[Dict[str, Any]],
            layout_override: Optional[Dict[str, Any]],
            dynamic_spacing: bool
    ) -> Tuple[Theme, Layout]:
        """
        Create theme and layout with overrides and optional dynamic spacing.

        Args:
            cv_data: CV data object
            theme_override: Theme overrides
            layout_override: Layout overrides
            dynamic_spacing: Whether to apply dynamic spacing

        Returns:
            Tuple of Theme and Layout objects
        """
        # Create theme with overrides
        theme_data = cv_data.get_theme_data()
        if theme_override:
            theme_data.update(theme_override)
        theme = Theme.from_dict(theme_data)

        # Create layout with overrides
        layout_data = cv_data.get_layout_data()
        if layout_override:
            layout_data.update(layout_override)

        # Apply dynamic spacing if enabled
        if dynamic_spacing:
            layout_data = self._apply_dynamic_spacing(cv_data, layout_data)

        layout = Layout.from_dict(layout_data)

        return theme, layout

    def _apply_dynamic_spacing(self, cv_data: CVData, layout_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply dynamic spacing based on content density.

        Args:
            cv_data: CV data object
            layout_data: Layout data dictionary

        Returns:
            Updated layout data dictionary
        """
        # Calculate content density
        content_density = self._calculate_content_density(cv_data)

        # Adjust spacing based on content density
        if content_density > 0.8:  # Very dense content
            # Reduce spacing to fit more content
            layout_data["section_spacing"] = 0.2 * inch
            layout_data["line_spacing"] = 10
            layout_data["paragraph_spacing"] = 0.08 * inch
            logger.debug("Applied compact spacing for dense content")
        elif content_density < 0.4:  # Sparse content
            # Increase spacing for better aesthetics
            layout_data["section_spacing"] = 0.4 * inch
            layout_data["line_spacing"] = 12
            layout_data["paragraph_spacing"] = 0.15 * inch
            logger.debug("Applied expanded spacing for sparse content")
        else:
            # Balanced spacing
            layout_data["section_spacing"] = 0.3 * inch
            layout_data["line_spacing"] = 11
            layout_data["paragraph_spacing"] = 0.12 * inch
            logger.debug("Applied balanced spacing for moderate content")

        return layout_data

    def _calculate_content_density(self, cv_data: CVData) -> float:
        """
        Calculate content density to determine optimal spacing.

        Args:
            cv_data: CV data object

        Returns:
            Content density score (0-1)
        """
        # Count characters in profile
        profile_length = len(cv_data.get_profile_data())

        # Count experience items
        experience_data = cv_data.get_experience_data()
        experience_count = len(experience_data.get("companies", []))

        # Count role descriptions
        roles_count = 0
        responsibilities_count = 0
        for company in experience_data.get("companies", []):
            roles_count += len(company.get("roles", []))
            for role in company.get("roles", []):
                responsibilities_count += len(role.get("responsibilities", []))

        # Count education items
        education_count = len(cv_data.get_education_data().get("items", []))

        # Count projects
        projects_count = len(cv_data.get_projects_data())

        # Calculate weighted score
        total_score = (
                profile_length * 0.1 / 1000 +  # Normalize by expected length
                experience_count * 0.3 / 4 +  # Normalize by expected count
                roles_count * 0.2 / 6 +  # Normalize by expected count
                responsibilities_count * 0.2 / 15 +  # Normalize by expected count
                education_count * 0.1 / 3 +  # Normalize by expected count
                projects_count * 0.1 / 4  # Normalize by expected count
        )

        # Clamp between 0 and 1
        density = max(0, min(1, total_score))
        logger.debug(f"Calculated content density: {density:.2f}")

        return density

    def _optimize_cv_content(self, cv_data: CVData) -> CVData:
        """
        Optimize CV content for better layout.
        This might include truncating long texts or limiting list items.

        Args:
            cv_data: CVData object

        Returns:
            Optimized CVData object
        """
        # Create a deep copy to avoid modifying the original CVData object
        optimized_data = CVData(debug_mode=cv_data.debug_mode)
        optimized_data.data = copy.deepcopy(cv_data.data)

        # Standardize date formats
        date_format = "%Y-%m-%d" # Example format
        for section_key in ["experience", "education"]:
            if section_key in optimized_data.data:
                items = optimized_data.data[section_key].get("items", []) # For education
                if section_key == "experience":
                    items = []
                    for company in optimized_data.data[section_key].get("companies", []):
                        items.extend(company.get("roles", []))
                
                for item in items:
                    if "startDate" in item and item["startDate"]:
                        try:
                            item["startDate"] = datetime.strptime(item["startDate"], date_format).strftime(date_format)
                        except ValueError:
                            logger.warning(f"Could not parse startDate: {item['startDate']} in {section_key}")
                    if "endDate" in item and item["endDate"]:
                        try:
                            item["endDate"] = datetime.strptime(item["endDate"], date_format).strftime(date_format)
                        except ValueError:
                            logger.warning(f"Could not parse endDate: {item['endDate']} in {section_key}")
                            
        logger.debug("CV content optimization (dates standardized, no truncation applied as per new requirement)")
        return optimized_data # Return optimized_data directly without further truncation

        # The following truncation logic is now disabled based on user request
        # to load all information.

        # # Optimize experience section
        # if "experience" in optimized_data.data:
        #     experience = optimized_data.data["experience"]
        #     for company in experience.get("companies", []):
        #         for role in company.get("roles", []):
        #             responsibilities = role.get("responsibilities", [])
        #             for i, resp in enumerate(responsibilities):
        #                 if len(resp) > 150: # Too long for one line
        #                     # Truncate at word boundary
        #                     truncated = resp[:147].rsplit(' ', 1)[0] + "..."
        #                     # Add ellipsis if not ending with punctuation
        #                     if not truncated.endswith(('.', '!', '?')):\n                                truncated += '.'
        #                     responsibilities[i] = truncated
        #                     logger.debug(f"Truncated long responsibility: {resp[:20]}...")

        # # Optimize projects section
        # if "projects" in optimized_data.data:
        #     projects = optimized_data.data["projects"]
        #     for project in projects:
        #         description = project.get("description", "")

        #         # Truncate overly long project descriptions
        #         if len(description) > 200:  # Too long for good layout
        #             # Truncate at a good break point
        #             truncated = description[:195].rsplit('.', 1)[0]
        #             if not truncated.endswith('.'):\n                        truncated += '.'
        #             project["description"] = truncated
        #             logger.debug(f"Truncated long project description: {description[:20]}...")

        # # Balance education items if too many
        # if "education" in optimized_data.data:
        #     education_items = optimized_data.data["education"].get("items", [])
        #     if len(education_items) > 3:
        #         # Keep only the most relevant (usually the most recent)
        #         optimized_data.data["education"]["items"] = education_items[:3]
        #         logger.debug(f"Limited education items to 3 (from {len(education_items)})")

        # # Balance technical skills to avoid overwhelming sections
        # if "technical_skills" in optimized_data.data:
        #     skills = optimized_data.data["technical_skills"]
        #     for category, skill_list in skills.items():
        #         if len(skill_list) > 5:
        #             # Keep only the top skills
        #             skills[category] = skill_list[:5]
        #             logger.debug(f"Limited skills in '{category}' to 5 (from {len(skill_list)})")

        # return optimized_data

    def get_template_info(self, template_name: Optional[str] = None) -> Union[Dict[str, Any], List[str]]:
        """
        Get information about available templates.

        Args:
            template_name: Name of template to get info for, or None for list of templates

        Returns:
            Dictionary with template information or list of template names
        """
        if template_name:
            template = self.template_manager.get_template(template_name)
            if template:
                return {
                    "name": template_name,
                    "description": getattr(template, "__doc__", "No description available"),
                    "features": getattr(template, "features", ["No features listed"])
                }
            else:
                logger.warning(f"Template '{template_name}' not found")
                return {}
        else:
            return self.template_manager.list_templates()

    def list_templates(self) -> List[str]:
        """Return a list of available template names."""
        templates = self.template_manager.list_templates()
        logger.debug(f"Available templates: {templates}")
        return templates

    def validate_cv_data(self, data_path: str) -> Tuple[bool, str]:
        """
        Validate CV data without generating PDF.

        Args:
            data_path: Path to CV data JSON

        Returns:
            Tuple of (validity, error_message)
        """
        if not os.path.exists(data_path):
            return False, f"CV data file not found: {data_path}"

        try:
            # Check if file is valid JSON
            with open(data_path, 'r', encoding='utf-8') as f:
                json.load(f)

            # Try loading with CV data class
            cv_data = CVData()
            cv_data.load(data_path)
            cv_data.validate()

            return True, "CV data is valid"
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON file: {e}")
            return False, f"Invalid JSON file: {str(e)}"
        except Exception as e:
            logger.error(f"Error validating CV data: {e}")
            return False, f"Error validating CV data: {str(e)}"

    def generate_preview(
            self,
            data_path: str,
            output_path: str,
            template_name: str = "minimal",
            profile_picture_path: Optional[str] = None
    ) -> str:
        """
        Generate a simplified preview CV.

        Args:
            data_path: Path to CV data JSON
            output_path: Where to save the PDF
            template_name: Name of the template to use (minimal works best for previews)
            profile_picture_path: Optional path to profile picture

        Returns:
            Path to the generated preview PDF
        """
        # Create a simplified output with minimal content for preview
        logger.info(f"Generating preview with template '{template_name}'")

        # Load CV data
        cv_data = CVData()
        cv_data.load(data_path)

        # Simplify data for preview
        preview_data = self._create_preview_data(cv_data)

        # Create temp JSON file for preview data
        preview_data_path = output_path + ".preview_data.json"
        with open(preview_data_path, 'w', encoding='utf-8') as f:
            json.dump(preview_data, f, indent=2)

        try:
            # Generate preview CV
            preview_output = output_path.replace(".pdf", "_preview.pdf")
            self.create_cv(
                data_path=preview_data_path,
                output_path=preview_output,
                template_name=template_name,
                profile_picture_path=profile_picture_path,
                content_optimization=True,
                dynamic_spacing=True
            )

            # Clean up temporary file
            os.remove(preview_data_path)

            return preview_output
        except Exception as e:
            logger.error(f"Error generating preview: {e}")
            # Clean up temporary file
            if os.path.exists(preview_data_path):
                os.remove(preview_data_path)
            raise

    def _create_preview_data(self, cv_data: CVData) -> Dict[str, Any]:
        """
        Create simplified data for preview.

        Args:
            cv_data: Original CV data

        Returns:
            Dictionary with simplified preview data
        """
        preview_data = {}

        # Include basic candidate info
        preview_data["candidate"] = cv_data.data.get("candidate", {})

        # Truncate profile text
        profile_text = cv_data.get_profile_data()
        if profile_text:
            if len(profile_text) > 200:
                preview_data["profile"] = profile_text[:200] + "..."
            else:
                preview_data["profile"] = profile_text

        # Include first few technical skills
        if "technical_skills" in cv_data.data:
            preview_data["technical_skills"] = {}
            for category, skills in cv_data.data["technical_skills"].items():
                preview_data["technical_skills"][category] = skills[:3]  # Only first 3 skills

        # Include most recent experience
        if "experience" in cv_data.data:
            preview_data["experience"] = {"companies": []}
            companies = cv_data.data["experience"].get("companies", [])
            if companies:
                # Add just the first company with limited roles
                first_company = companies[0].copy()
                if "roles" in first_company:
                    first_company["roles"] = first_company["roles"][:1]  # Only first role
                    # Limit responsibilities
                    for role in first_company["roles"]:
                        if "responsibilities" in role:
                            role["responsibilities"] = role["responsibilities"][:2]  # Only first 2 responsibilities
                preview_data["experience"]["companies"].append(first_company)

        # Include most recent education
        if "education" in cv_data.data:
            preview_data["education"] = {"items": []}
            education_items = cv_data.data["education"].get("items", [])
            if education_items:
                preview_data["education"]["items"] = [education_items[0]]  # Only first education item

        # Include theme settings
        if "theme" in cv_data.data:
            preview_data["theme"] = cv_data.data["theme"]

        # Include layout settings
        if "layout" in cv_data.data:
            preview_data["layout"] = cv_data.data["layout"]

        return preview_data

    def _adjust_theme_for_content_density(self, content_density: float) -> Theme:
        """
        Adjust theme settings based on content density.
        
        Args:
            content_density: Content density score (0-1)
            
        Returns:
            Adjusted Theme object
        """
        # Default theme values
        primary_color = "#003087"
        secondary_color = "#0070CC"
        accent_color = "#BEDCF9"
        background_color = "#F5F8FC"
        text_color = "#333333"
        header_font = "Helvetica-Bold"
        body_font = "Helvetica"
        section_spacing = 0.3 * inch
        paragraph_spacing = 0.12 * inch
        
        # Adjust font sizes and spacing based on content density
        if content_density > 0.8:  # Very dense content
            # Use smaller fonts and tighter spacing
            header_font_size = 13  # Increased from 11
            body_font_size = 11    # Increased from 9
            line_spacing = 12      # Increased from 10
            section_spacing = 0.25 * inch
            paragraph_spacing = 0.1 * inch
            logger.debug("Using smaller fonts and tighter spacing for dense content")
        elif content_density < 0.4:  # Sparse content
            # Use larger fonts and more generous spacing
            header_font_size = 16  # Increased from 14
            body_font_size = 12    # Increased from 10
            line_spacing = 14      # Increased from 12
            section_spacing = 0.35 * inch
            paragraph_spacing = 0.15 * inch
            logger.debug("Using larger fonts and more spacing for sparse content")
        else:
            # Use default sizes
            header_font_size = 14  # Increased from 12
            body_font_size = 11.5  # Increased from 9.5
            line_spacing = 13      # Increased from 11
            logger.debug("Using default fonts for moderate content")
        
        # Create and return the theme with all required parameters
        theme = Theme(
            primary_color=primary_color,
            secondary_color=secondary_color,
            accent_color=accent_color,
            background_color=background_color,
            text_color=text_color,
            header_font=header_font,
            body_font=body_font,
            header_font_size=header_font_size,
            body_font_size=body_font_size,
            section_spacing=section_spacing,
            line_spacing=line_spacing,
            paragraph_spacing=paragraph_spacing
        )
            
        return theme
        
    def _get_template_by_name(self, template_name: str):
        """
        Get a template instance by name.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Template instance
            
        Raises:
            ValueError: If template not found
        """
        template = self.template_manager.get_template(template_name)
        if template is None:
            available_templates = self.template_manager.list_templates()
            logger.error(f"Template '{template_name}' not found. Available templates: {available_templates}")
            raise ValueError(f"Template '{template_name}' not found. Available templates: {available_templates}")
        return template


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate a CV from JSON data")
    parser.add_argument("data", help="Path to the CV data JSON file")
    parser.add_argument("output", help="Output PDF file path")
    parser.add_argument("--template", "-t", default="two_column", help="Template to use")
    parser.add_argument("--profile-picture", "-p", help="Path to profile picture")
    # Add color customization options
    parser.add_argument("--primary-color", help="Primary color override (e.g., #003087)")
    parser.add_argument("--secondary-color", help="Secondary color override (e.g., #0070CC)")
    parser.add_argument("--accent-color", help="Accent color override (e.g., #BEDCF9)")
    parser.add_argument("--background-color", help="Background color override (e.g., #F5F8FC)")
    parser.add_argument("--text-color", help="Text color override (e.g., #333333)")
    parser.add_argument("--list-templates", "-l", action="store_true",
                        help="List available templates and exit")
    parser.add_argument("--validate", "-v", action="store_true",
                        help="Validate the CV data file without generating PDF")
    parser.add_argument("--preview", action="store_true",
                        help="Generate a simplified preview")
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug mode for additional logging")

    args = parser.parse_args()

    generator = CVGenerator(debug_mode=args.debug)

    # List templates if requested
    if args.list_templates:
        templates = generator.list_templates()
        print("Available templates:")
        for template in templates:
            print(f"  - {template}")
        exit()

    # Validate CV data if requested
    if args.validate:
        valid, message = generator.validate_cv_data(args.data)
        print(message)
        exit(0 if valid else 1)

    # Generate CV
    try:
        generator.create_cv(
            data_path=args.data,
            output_path=args.output,
            template_name=args.template,
            profile_picture_path=args.profile_picture
        )
        print(f"CV generated successfully: {args.output}")
    except Exception as e:
        logger.error(f"Error generating CV: {e}")
        exit(1)