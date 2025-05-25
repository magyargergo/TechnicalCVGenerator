#!/usr/bin/env python3
"""
Example usage script for the CV Generator.
This script provides a command-line interface to generate CVs using different templates.
"""

import argparse
import os
import sys
from pathlib import Path

from cv_generator import CVGenerator
from cv_data import CVData
from theme import Theme
from layout import Layout


def list_available_templates():
    """List all available templates."""
    templates = ["two_column", "minimal", "modern"]
    print("Available templates:")
    for template in templates:
        print(f"  - {template}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a CV using the flexible CV Generator"
    )
    
    parser.add_argument(
        "--data", "-d",
        type=str,
        default="cv_data.json",
        help="Path to CV data JSON file (default: cv_data.json)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="output/generated_cv.pdf",
        help="Output PDF file path (default: output/generated_cv.pdf)"
    )
    
    parser.add_argument(
        "--template", "-t",
        type=str,
        default="two_column",
        choices=["two_column", "minimal", "modern"],
        help="Template to use (default: two_column)"
    )
    
    parser.add_argument(
        "--profile-picture", "-p",
        type=str,
        help="Path to profile picture (optional)"
    )
    
    parser.add_argument(
        "--list-templates", "-l",
        action="store_true",
        help="List available templates and exit"
    )
    
    parser.add_argument(
        "--primary-color",
        type=str,
        help="Primary color override (e.g., #003087)"
    )
    
    parser.add_argument(
        "--accent-color",
        type=str,
        help="Accent color override (e.g., #BEDCF9)"
    )
    
    args = parser.parse_args()
    
    # List templates and exit if requested
    if args.list_templates:
        list_available_templates()
        return 0
    
    # Check if data file exists
    if not os.path.exists(args.data):
        print(f"Error: CV data file '{args.data}' not found.")
        return 1
    
    # Check if profile picture exists (if provided)
    if args.profile_picture and not os.path.exists(args.profile_picture):
        print(f"Error: Profile picture '{args.profile_picture}' not found.")
        return 1
    
    try:
        # Load CV data
        cv_data = CVData(args.data)
        
        # Create theme with potential overrides
        theme = Theme()
        if args.primary_color:
            theme.primary_color = args.primary_color
        if args.accent_color:
            theme.accent_color = args.accent_color
        
        # Create layout
        layout = Layout()
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(args.output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Initialize CV generator
        generator = CVGenerator(cv_data, theme, layout)
        
        # Set profile picture if provided
        if args.profile_picture:
            generator.profile_picture_path = args.profile_picture
        
        # Generate CV
        print(f"Generating CV using '{args.template}' template...")
        generator.generate(args.output, template_name=args.template)
        print(f"CV successfully generated: {args.output}")
        
        return 0
        
    except Exception as e:
        print(f"Error generating CV: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 