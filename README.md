# Modern CV Generator

A flexible, dynamic, and easily customizable CV generation system built with Python and ReportLab. This system allows you to maintain your CV data in a single JSON file and generate professional PDFs in multiple layouts without duplicating content.

## Features

- **Data-Driven Design**: Keep all your CV content in a single JSON file that's easy to update
- **Multiple Templates**: Choose from several built-in templates (two-column, minimal, modern)
- **Customizable Themes**: Override colors and styling without editing code
- **Modular Architecture**: Easily extend with new templates and components
- **Automatic Page Breaks**: Smart handling of content across multiple pages
- **Icon Support**: Font Awesome integration for professional iconography
- **Profile Picture**: Optional circular profile image support

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/TechnicalCVGenerator.git
cd TechnicalCVGenerator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Generate your first CV:
```bash
python example_usage.py --data cv_data_example.json --output my_cv.pdf
```

4. Customize the example data file (`cv_data_example.json`) with your information and regenerate.

## Architecture

The system follows a modular, object-oriented architecture:

- **CVGenerator**: Main class that orchestrates the CV generation process
- **CVData**: Handles loading, validation, and access to CV content
- **Theme**: Manages visual styling (colors, fonts, spacing)
- **Layout**: Controls physical layout parameters (page size, margins, columns)
- **Templates**: Interchangeable layout implementations
- **Utilities**: Text processing for wrapping and hyphenation

## Getting Started

### Prerequisites

- Python 3.6+
- ReportLab (`pip install reportlab`)
- Pyphen for hyphenation (`pip install pyphen`)
- Requests for font downloading (`pip install requests`)
- Pillow for image processing (`pip install Pillow`)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/TechnicalCVGenerator.git
cd TechnicalCVGenerator

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

1. Create your CV data JSON file (see [Data Format](#data-format) below)
2. Run the generator:

```bash
python example_usage.py --data cv_data.json --output my_cv.pdf --template two_column
```

### Command Line Options

```
usage: example_usage.py [-h] [--data DATA] [--output OUTPUT] [--template TEMPLATE]
                      [--profile-picture PROFILE_PICTURE] [--list-templates]
                      [--primary-color PRIMARY_COLOR] [--accent-color ACCENT_COLOR]

Generate a CV using the flexible CV Generator

optional arguments:
  -h, --help            show this help message and exit
  --data DATA, -d DATA  Path to CV data JSON file (default: cv_data.json)
  --output OUTPUT, -o OUTPUT
                        Output PDF file path (default: output/generated_cv.pdf)
  --template TEMPLATE, -t TEMPLATE
                        Template to use (default: two_column)
  --profile-picture PROFILE_PICTURE, -p PROFILE_PICTURE
                        Path to profile picture (optional)
  --list-templates, -l  List available templates and exit
  --primary-color PRIMARY_COLOR
                        Primary color override (e.g., #003087)
  --accent-color ACCENT_COLOR
                        Accent color override (e.g., #BEDCF9)
```

## Available Templates

### Two Column Template
Traditional CV layout with a left sidebar and a right main content area. Good for detailed CVs with multiple sections.

### Minimal Template 
Clean, minimalist design with a single column layout. Perfect for simple CVs or when you want to maximize content space.

### Modern Template
Contemporary design with a bold sidebar and elegant main content area. Features a prominent name display and vibrant section headers.

## Data Format

Your CV data should be in JSON format. See `cv_data_example.json` for a complete example. Here's a simplified structure:

```json
{
  "candidate": {
    "name": "John Doe",
    "contact": [
      {"icon": "\uf0e0", "text": "Email: john.doe@example.com"},
      {"icon": "\uf041", "text": "London, United Kingdom"},
      {"icon": "\uf095", "text": "Phone: +44 123 456 7890"},
      {"icon": "\uf08c", "text": "LinkedIn: linkedin.com/in/johndoe"}
    ]
  },
  "profile": "Senior Software Engineer with 7+ years of experience...",
  "technical_skills": {
    "Frontend Development": ["React", "Angular", "JavaScript"],
    "Backend Development": ["Python", "Node.js", "SQL"]
  },
  "education": {
    "items": [
      {
        "institution": "University of Example",
        "degree": "BSc Computer Science",
        "duration": "2010 - 2014"
      }
    ]
  },
  "experience": {
    "companies": [
      {
        "name": "Example Corp",
        "totalDuration": "3 years",
        "roles": [
          {
            "title": "Senior Developer",
            "responsibilities": [
              "Led development team of 5 engineers",
              "Implemented CI/CD pipeline"
            ]
          }
        ]
      }
    ]
  },
  "additional_info": [
    "Fluent in English and Spanish",
    "Available for remote work"
  ],
  "projects": [
    {
      "title": "Project Management System",
      "description": "Designed and implemented a web-based project management tool..."
    }
  ],
  "theme": {
    "primary_color": "#003087",
    "accent_color": "#BEDCF9" 
  }
}
```

### Font Awesome Icons

The contact section uses Font Awesome icons. Common icon codes:
- Email: `\uf0e0`
- Location: `\uf041`
- Phone: `\uf095`
- LinkedIn: `\uf08c`
- GitHub: `\uf09b`
- Website: `\uf0ac`

## Customization

### Adding a New Template

1. Create a new class that extends `BaseTemplate` in the templates directory
2. Implement the `render` method and any supporting methods
3. Register your template in `CVGenerator.register_default_templates()`

### Modifying the Theme

You can override theme settings in the JSON data or via command line arguments:

```bash
python example_usage.py --data cv_data.json --primary-color "#2C3E50" --accent-color "#3498DB"
```

## Project Structure

```
TechnicalCVGenerator/
├── cv_generator.py      # Main CV generator class
├── cv_data.py          # CV data handling
├── theme.py            # Theme configuration
├── layout.py           # Layout parameters
├── font_manager.py     # Font management
├── text_utils.py       # Text processing utilities
├── template_manager.py # Template registration
├── word_generator.py   # Word document generation
├── main.py            # Main entry point
├── example_usage.py   # CLI interface
├── templates/         # Template implementations
├── fonts/            # Font files
├── data/             # Sample data files
├── output/           # Generated PDFs (gitignored)
└── README.md         # This file
```

## Testing

Automated tests validate that the PDF generator works correctly. Generated PDF
files are converted to ASCII using `pdfminer.six` and compared against baseline
output stored under `tests/expected`. If the ASCII output differs from the
baseline a unified diff is shown. To run the tests install the dependencies and
execute `pytest`:

```bash
pip install -r requirements.txt
pip install pytest
pytest
```

If you intentionally change the PDF output, regenerate the baseline with:

```bash
python -m tests.generate_baseline
```

## Contributing

Contributions are welcome! Some ideas for improvements:

- Add more templates
- Support for additional fonts
- QR code generation for contact info
- Export to other formats (HTML, DOCX)
- Multilingual support for text processing
- Unit tests
- GitHub Actions for CI/CD

Please feel free to submit issues and pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.