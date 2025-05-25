#!/usr/bin/env python
"""
Main application entry point for CV Generator.
Offers both PDF and Word document generation.
"""
import os
import sys
import logging
import argparse
from typing import Optional

from cv_generator import CVGenerator
from word_generator import WordCVGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('main')

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate professional CV in PDF or Word format')
    parser.add_argument('data_path', help='Path to CV data JSON file')
    parser.add_argument('output_path', help='Path to save the generated document')
    parser.add_argument('--template', default='two_column', help='CV template to use (for PDF format)')
    parser.add_argument('--profile-picture', dest='profile_picture_path', help='Path to profile picture')
    parser.add_argument('--format', choices=['pdf', 'docx', 'both'], default='pdf', 
                        help='Output format: pdf, docx, or both')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Set debug level if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    # Validate input file
    if not os.path.exists(args.data_path):
        logger.error(f"CV data file not found: {args.data_path}")
        sys.exit(1)
    
    # Validate profile picture if provided
    if args.profile_picture_path and not os.path.exists(args.profile_picture_path):
        logger.error(f"Profile picture not found: {args.profile_picture_path}")
        sys.exit(1)
    
    # Generate documents based on format choice
    output_base = os.path.splitext(args.output_path)[0]
    
    try:
        if args.format in ['pdf', 'both']:
            pdf_path = f"{output_base}.pdf"
            logger.info(f"Generating PDF CV: {pdf_path}")
            pdf_generator = CVGenerator(debug_mode=args.debug)
            pdf_generator.create_cv(
                data_path=args.data_path,
                output_path=pdf_path,
                template_name=args.template,
                profile_picture_path=args.profile_picture_path
            )
            logger.info(f"PDF CV generated: {pdf_path}")
        
        if args.format in ['docx', 'both']:
            docx_path = f"{output_base}.docx"
            logger.info(f"Generating Word document CV: {docx_path}")
            word_generator = WordCVGenerator(debug_mode=args.debug)
            word_generator.create_cv(
                args.data_path,
                docx_path
            )
            logger.info(f"Word document CV generated: {docx_path}")
            
        logger.info("CV generation completed successfully")
        
    except Exception as e:
        logger.error(f"Error generating CV: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 