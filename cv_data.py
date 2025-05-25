#!/usr/bin/env python
"""
CV Data - Enhanced class for loading and handling CV data.
"""
import json
import os
import copy
import logging
from typing import Dict, Any, List, Optional, Tuple, Union

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('cv_data')


class CVData:
    """
    Enhanced class for handling CV data loading, validation, and access.
    Provides the interface to access CV content for templates to render.
    """

    def __init__(self, debug_mode: bool = False):
        """
        Initialize with empty data.

        Args:
            debug_mode: Enable debug logging
        """
        self.data = {}
        self.default_theme = {
            "primary_color": "#003087",  # Banner color
            "secondary_color": "#0070CC",  # Profile circle color
            "accent_color": "#BEDCF9",  # Section header color
            "background_color": "#F5F8FC",  # Left column background
            "text_color": "#333333",  # Main text color
            "header_font": "DejaVuSans-Bold",
            "body_font": "DejaVuSans",
            "header_font_size": 12,
            "body_font_size": 9.5
        }
        self.default_layout = {
            "page_size": "A4",
            "left_margin": 0.3,  # in inches
            "right_margin": 0.3,
            "top_margin": 0.4,
            "bottom_margin": 0.4,
            "banner_height": 1.4,  # in inches
            "left_column_width_ratio": 0.3,
            "section_spacing": 0.3,  # in inches
            "line_spacing": 11,  # in points
            "paragraph_spacing": 0.12  # in inches
        }
        self.schema = self._get_schema()

        # Set up logging
        self.debug_mode = debug_mode
        if self.debug_mode:
            logger.setLevel(logging.DEBUG)

        logger.debug("CVData initialized in debug mode")

    def _get_schema(self) -> Dict[str, Any]:
        """Define the expected CV data schema."""
        return {
            "required": ["candidate", "profile"],
            "sections": {
                "candidate": {
                    "required": ["name", "contact"]
                },
                "profile": {},
                "technical_skills": {},
                "education": {},
                "experience": {
                    "required": ["companies"]
                },
                "additional_info": {},
                "projects": {},
                "references": {},
                "theme": {},
                "layout": {}
            }
        }

    def load(self, file_path: str, debug_mode: bool = False) -> None:
        """
        Load CV data from a JSON file.

        Args:
            file_path: Path to the JSON file containing CV data
            debug_mode: Enable debug mode

        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file isn't valid JSON
        """
        # Set debug mode if requested
        if debug_mode:
            self.debug_mode = True
            logger.setLevel(logging.DEBUG)
            logger.debug(f"Debug mode enabled for loading file: {file_path}")

        if not os.path.exists(file_path):
            logger.error(f"CV data file not found: {file_path}")
            raise FileNotFoundError(f"CV data file not found: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
                logger.debug(f"CV data loaded successfully from {file_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format in file {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading CV data from {file_path}: {e}")
            raise

    def save(self, file_path: str) -> None:
        """
        Save CV data to a JSON file.

        Args:
            file_path: Path where to save the JSON file

        Raises:
            IOError: If the file can't be written
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2)
                logger.debug(f"CV data saved successfully to {file_path}")
        except Exception as e:
            logger.error(f"Error saving CV data to {file_path}: {e}")
            raise

    def validate(self) -> bool:
        """
        Validate the loaded data against the schema.

        Returns:
            True if data is valid

        Raises:
            ValueError: If data doesn't match the expected schema
        """
        # Check required top-level fields
        for field in self.schema["required"]:
            if field not in self.data:
                logger.error(f"Required field '{field}' missing from CV data")
                raise ValueError(f"Required field '{field}' missing from CV data")

        # Check section requirements
        for section, requirements in self.schema["sections"].items():
            if section in self.data and "required" in requirements:
                for required_field in requirements["required"]:
                    if required_field not in self.data[section]:
                        logger.error(f"Required field '{required_field}' missing from '{section}' section")
                        raise ValueError(f"Required field '{required_field}' missing from '{section}' section")

        # Validate specific sections format
        self._validate_contact_format()
        self._validate_experience_format()

        logger.debug("CV data validation successful")
        return True

    def _validate_contact_format(self) -> None:
        """
        Validate contact information format.

        Raises:
            ValueError: If contact format is invalid
        """
        if "candidate" in self.data and "contact" in self.data["candidate"]:
            contacts = self.data["candidate"]["contact"]
            if not isinstance(contacts, list):
                raise ValueError("Contact information should be a list")

            for item in contacts:
                if not isinstance(item, dict):
                    raise ValueError("Each contact item should be a dictionary")
                if "icon" not in item or "text" not in item:
                    raise ValueError("Contact items must contain 'icon' and 'text' fields")

    def _validate_experience_format(self) -> None:
        """
        Validate experience section format.

        Raises:
            ValueError: If experience format is invalid
        """
        if "experience" in self.data and "companies" in self.data["experience"]:
            companies = self.data["experience"]["companies"]
            if not isinstance(companies, list):
                raise ValueError("Companies should be a list")

            for company in companies:
                if not isinstance(company, dict):
                    raise ValueError("Each company should be a dictionary")
                if "name" not in company:
                    raise ValueError("Each company must have a 'name' field")
                if "roles" in company and not isinstance(company["roles"], list):
                    raise ValueError("Company roles should be a list")

    def copy(self) -> 'CVData':
        """
        Create a deep copy of the CV data object.

        Returns:
            A new CVData instance with copied data
        """
        new_cv_data = CVData(self.debug_mode)
        new_cv_data.data = copy.deepcopy(self.data)
        return new_cv_data

    def get_theme_data(self) -> Dict[str, Any]:
        """
        Get theme data, merging with defaults.

        Returns:
            Dictionary with theme settings
        """
        theme_data = self.default_theme.copy()
        if "theme" in self.data:
            theme_data.update(self.data["theme"])
        return theme_data

    def get_layout_data(self) -> Dict[str, Any]:
        """
        Get layout data, merging with defaults.

        Returns:
            Dictionary with layout settings
        """
        layout_data = self.default_layout.copy()
        if "layout" in self.data:
            layout_data.update(self.data["layout"])
        return layout_data

    def get_candidate_data(self) -> Dict[str, Any]:
        """
        Get candidate data.

        Returns:
            Dictionary with candidate information
        """
        return self.data.get("candidate", {})

    def get_profile_data(self) -> str:
        """
        Get profile text.

        Returns:
            Profile text as string
        """
        return self.data.get("profile", "")

    def get_technical_skills(self) -> Dict[str, List[str]]:
        """
        Get technical skills data.

        Returns:
            Dictionary mapping skill categories to lists of skills
        """
        return self.data.get("technical_skills", {})

    def get_education_data(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Get education data.

        Returns:
            Dictionary with education items
        """
        return self.data.get("education", {"items": []})

    def get_experience_data(self) -> Dict[str, Any]:
        """
        Get experience data.

        Returns:
            Dictionary with experience information
        """
        return self.data.get("experience", {"companies": []})

    def get_additional_info(self) -> List[str]:
        """
        Get additional information.

        Returns:
            List of additional information items
        """
        return self.data.get("additional_info", [])

    def get_projects_data(self) -> List[Dict[str, str]]:
        """
        Get projects data.

        Returns:
            List of project dictionaries
        """
        return self.data.get("projects", [])

    def get_references(self) -> str:
        """
        Get references data.

        Returns:
            References text
        """
        return self.data.get("references", "References available upon request.")

    def get_section_data(self, section_name: str) -> Any:
        """
        Get data for a specific section.

        Args:
            section_name: Name of the section to retrieve

        Returns:
            The section data or None if not found
        """
        return self.data.get(section_name)

    def has_section(self, section_name: str) -> bool:
        """
        Check if the data contains a specific section.

        Args:
            section_name: Name of section to check

        Returns:
            True if section exists and has content
        """
        return section_name in self.data and self.data[section_name]

    def update_section(self, section_name: str, section_data: Any) -> None:
        """
        Update or create a section with the provided data.

        Args:
            section_name: Name of section to update
            section_data: New data for the section
        """
        self.data[section_name] = section_data
        logger.debug(f"Updated section '{section_name}'")

    def get_content_density(self) -> float:
        """
        Calculate content density to determine optimal spacing.

        Returns:
            Content density score (0-1)
        """
        # Count characters in profile
        profile_length = len(self.get_profile_data())

        # Count experience items
        experience_data = self.get_experience_data()
        experience_count = len(experience_data.get("companies", []))

        # Count role descriptions
        roles_count = 0
        responsibilities_count = 0
        for company in experience_data.get("companies", []):
            roles_count += len(company.get("roles", []))
            for role in company.get("roles", []):
                responsibilities_count += len(role.get("responsibilities", []))

        # Count education items
        education_count = len(self.get_education_data().get("items", []))

        # Count projects
        projects_count = len(self.get_projects_data())

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

    def optimize_content(self) -> None:
        """
        Optimize content for better layout by adjusting text lengths, adding paragraph breaks, etc.
        """
        logger.debug("Optimizing CV content")

        # Optimize profile text
        profile_text = self.get_profile_data()
        # Ensure profile has paragraph breaks for better readability
        if profile_text and "\n\n" not in profile_text and len(profile_text) > 300:
            # Find good break points (after sentences) and add paragraph breaks
            sentences = profile_text.split('. ')
            if len(sentences) >= 3:
                # Add paragraph break after every 2-3 sentences
                paragraph_breaks = []
                current_paragraph = []
                for i, sentence in enumerate(sentences):
                    current_paragraph.append(sentence)
                    if i > 0 and (i + 1) % 2 == 0 and i < len(sentences) - 1:
                        paragraph_breaks.append('. '.join(current_paragraph) + '.')
                        current_paragraph = []
                if current_paragraph:
                    paragraph_breaks.append('. '.join(current_paragraph))

                self.data["profile"] = '\n\n'.join(paragraph_breaks)
                logger.debug("Added paragraph breaks to profile text")

        # Optimize experience section
        if "experience" in self.data:
            companies = self.data["experience"].get("companies", [])
            for company in companies:
                for role in company.get("roles", []):
                    responsibilities = role.get("responsibilities", [])

                    # Truncate overly long responsibility descriptions
                    for i, resp in enumerate(responsibilities):
                        if len(resp) > 150:  # Too long for good layout
                            # Truncate at a good break point
                            truncated = resp[:145].rsplit(',', 1)[0]
                            if not truncated.endswith('.'):
                                truncated += '.'
                            responsibilities[i] = truncated
                            logger.debug(f"Truncated long responsibility: {resp[:20]}...")

        # Optimize projects section
        if "projects" in self.data:
            projects = self.data["projects"]
            for project in projects:
                description = project.get("description", "")

                # Truncate overly long project descriptions
                if len(description) > 200:  # Too long for good layout
                    # Truncate at a good break point
                    truncated = description[:195].rsplit('.', 1)[0]
                    if not truncated.endswith('.'):
                        truncated += '.'
                    project["description"] = truncated
                    logger.debug(f"Truncated long project description: {description[:20]}...")

    def create_preview_data(self) -> Dict[str, Any]:
        """
        Create simplified data for preview.

        Returns:
            Dictionary with simplified preview data
        """
        logger.debug("Creating preview data")
        preview_data = {}

        # Include basic candidate info
        preview_data["candidate"] = self.get_candidate_data()

        # Truncate profile text
        profile_text = self.get_profile_data()
        if profile_text:
            if len(profile_text) > 200:
                preview_data["profile"] = profile_text[:200] + "..."
            else:
                preview_data["profile"] = profile_text

        # Include first few technical skills
        if "technical_skills" in self.data:
            preview_data["technical_skills"] = {}
            for category, skills in self.data["technical_skills"].items():
                preview_data["technical_skills"][category] = skills[:3]  # Only first 3 skills

        # Include most recent experience
        if "experience" in self.data:
            preview_data["experience"] = {"companies": []}
            companies = self.data["experience"].get("companies", [])
            if companies:
                # Add just the first company with limited roles
                first_company = copy.deepcopy(companies[0])
                if "roles" in first_company:
                    first_company["roles"] = first_company["roles"][:1]  # Only first role
                    # Limit responsibilities
                    for role in first_company["roles"]:
                        if "responsibilities" in role:
                            role["responsibilities"] = role["responsibilities"][:2]  # Only first 2 responsibilities
                preview_data["experience"]["companies"].append(first_company)

        # Include most recent education
        if "education" in self.data:
            preview_data["education"] = {"items": []}
            education_items = self.data["education"].get("items", [])
            if education_items:
                preview_data["education"]["items"] = [education_items[0]]  # Only first education item

        # Include theme settings
        if "theme" in self.data:
            preview_data["theme"] = self.data["theme"]

        # Include layout settings
        if "layout" in self.data:
            preview_data["layout"] = self.data["layout"]

        return preview_data

    def merge(self, other_data: Dict[str, Any]) -> None:
        """
        Merge data from another source into this CV data.

        Args:
            other_data: Dictionary with data to merge
        """
        # Use a deep merge strategy
        self._deep_merge(self.data, other_data)
        logger.debug("Merged external data into CV data")

    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Recursively merge source dictionary into target dictionary.

        Args:
            target: Target dictionary to merge into
            source: Source dictionary to merge from
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                # Recursively merge subdictionaries
                self._deep_merge(target[key], value)
            elif key in target and isinstance(target[key], list) and isinstance(value, list):
                # For lists, append new items or replace existing ones
                target[key].extend(value)
            else:
                # For everything else, just replace the value
                target[key] = copy.deepcopy(value)

    def get_section_count(self) -> int:
        """
        Get the count of non-empty sections.

        Returns:
            Number of sections with content
        """
        section_count = 0
        for section in self.schema["sections"]:
            if self.has_section(section):
                section_count += 1
        return section_count

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the CV data.

        Returns:
            Dictionary with CV statistics
        """
        stats = {
            "section_count": self.get_section_count(),
            "profile_length": len(self.get_profile_data()),
            "companies_count": len(self.get_experience_data().get("companies", [])),
            "education_count": len(self.get_education_data().get("items", [])),
            "projects_count": len(self.get_projects_data()),
            "technical_skills_categories": len(self.get_technical_skills()),
            "content_density": self.get_content_density()
        }

        # Calculate total number of skills
        total_skills = 0
        for category, skills in self.get_technical_skills().items():
            total_skills += len(skills)
        stats["total_skills"] = total_skills

        # Calculate total responsibilities
        total_responsibilities = 0
        for company in self.get_experience_data().get("companies", []):
            for role in company.get("roles", []):
                total_responsibilities += len(role.get("responsibilities", []))
        stats["total_responsibilities"] = total_responsibilities

        return stats