# Contributing to MyCRM

First off, thank you for considering contributing to MyCRM! It's people like you that make MyCRM such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps which reproduce the problem**
* **Provide specific examples to demonstrate the steps**
* **Describe the behavior you observed after following the steps**
* **Explain which behavior you expected to see instead and why**
* **Include screenshots and animated GIFs** if possible

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a step-by-step description of the suggested enhancement**
* **Provide specific examples to demonstrate the steps**
* **Describe the current behavior** and **explain which behavior you expected to see instead**
* **Explain why this enhancement would be useful**

### Pull Requests

* Fill in the required template
* Do not include issue numbers in the PR title
* Follow the Python and TypeScript/JavaScript styleguides
* Include thoughtfully-worded, well-structured tests
* Document new code
* End all files with a newline

## Development Setup

1. Fork the repo
2. Clone your fork
3. Create a branch for your feature/fix
4. Make your changes
5. Run tests
6. Push to your fork
7. Submit a pull request

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py test
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
npm run test
```

## Styleguides

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

### Python Styleguide

* Follow PEP 8
* Use descriptive variable names
* Add docstrings to functions and classes
* Keep functions small and focused

### JavaScript/TypeScript Styleguide

* Use ES6+ features
* Use TypeScript for type safety
* Follow the existing code style
* Use meaningful variable and function names

### Documentation Styleguide

* Use Markdown
* Reference functions, classes, and modules with backticks
* Include code examples where appropriate

## Questions?

Feel free to open an issue with your question or reach out to the maintainers directly.

Thank you for your contributions! 🎉
