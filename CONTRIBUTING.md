# Contributing to Technical CV Generator

Thank you for your interest in contributing to the Technical CV Generator! This document provides guidelines and instructions for contributing to the project.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/TechnicalCVGenerator.git
   cd TechnicalCVGenerator
   ```
3. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. Install the development dependencies:
   ```bash
   pip install -r requirements.txt
   pip install flake8 pytest  # For linting and testing
   ```

## Development Guidelines

### Code Style

- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep line length under 120 characters
- Run `flake8` before committing to check for style issues

### Testing

- Test your changes with different CV data configurations
- Ensure all templates work with your changes
- Add test cases for new features when applicable

### Commit Messages

- Use clear and descriptive commit messages
- Start with a verb in present tense (e.g., "Add", "Fix", "Update")
- Keep the first line under 50 characters
- Add detailed description if needed after a blank line

Example:
```
Add support for custom fonts

- Implement font loading from user-specified paths
- Add validation for font file formats
- Update documentation with font usage examples
```

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in the Issues section
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version)
   - Error messages or logs if applicable

### Suggesting Features

1. Check existing issues for similar suggestions
2. Create a new issue with the "enhancement" label
3. Describe the feature and its use case
4. Provide examples if possible

### Submitting Pull Requests

1. Make your changes in a feature branch
2. Ensure your code follows the style guidelines
3. Test your changes thoroughly
4. Update documentation if needed
5. Push to your fork and create a pull request
6. Describe your changes in the PR description
7. Link any related issues

### Areas for Contribution

Here are some areas where contributions are particularly welcome:

- **New Templates**: Create new CV templates with different layouts
- **Font Support**: Expand font options and management
- **Export Formats**: Add support for HTML, DOCX, or other formats
- **Internationalization**: Add support for multiple languages
- **Performance**: Optimize PDF generation for large CVs
- **Testing**: Add unit tests and integration tests
- **Documentation**: Improve or translate documentation
- **Examples**: Add more example CV data files

## Template Development

To create a new template:

1. Create a new file in the `templates/` directory
2. Inherit from the `BaseTemplate` class
3. Implement the required methods:
   - `render()`: Main rendering method
   - Any helper methods for sections
4. Register your template in `CVGenerator.register_default_templates()`
5. Add an example showcasing your template

Example template structure:
```python
from templates.base_template import BaseTemplate

class MyTemplate(BaseTemplate):
    def render(self, c, cv_data, theme, layout):
        # Your rendering logic here
        pass
```

## Questions?

If you have questions about contributing, feel free to:
- Open an issue for discussion
- Check existing documentation
- Review similar pull requests

Thank you for helping make Technical CV Generator better! 