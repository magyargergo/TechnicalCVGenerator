#!/usr/bin/env python
"""
Template Manager - Class for managing CV templates.
"""
from typing import Dict, Any, List, Optional


class TemplateManager:
    """
    Manages CV templates with registration and retrieval functionality.
    """

    def __init__(self):
        """Initialize with an empty template registry."""
        self.templates = {}

    def register_template(self, name: str, template: Any) -> None:
        """
        Register a template with a name.

        Args:
            name: Template identifier
            template: Template object
        """
        self.templates[name] = template

    def get_template(self, name: str) -> Optional[Any]:
        """
        Get a template by name.

        Args:
            name: Template identifier

        Returns:
            The template object or None if not found
        """
        return self.templates.get(name)

    def list_templates(self) -> List[str]:
        """
        Get a list of available template names.

        Returns:
            List of template names
        """
        return list(self.templates.keys())