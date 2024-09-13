# Contributing to A.D.I.

We appreciate your interest in contributing to A.D.I.! To maintain the quality of the project and ensure smooth collaboration, please follow the guidelines below.

## Prerequisites

A.D.I. is built using Python, and we use [Poetry](https://python-poetry.org/) to manage dependencies and packaging. Make sure you have the following installed on your machine:

- Python 3.8+
- Poetry (latest version)

### Setting up Your Development Environment

1. **Fork the Repository:**
Fork the A.D.I. repository to your GitHub account and clone it to your local machine.

```bash
git clone https://github.com/aditya30051993/A.D.I.git
cd A.D.I
```

2. **Install Dependencies:**
Install project dependencies using Poetry.

```bash
poetry install
```

3. **Activate the Virtual Environment:**
Activate the virtual environment created by Poetry.

```bash
poetry shell
```

4. **Run Tests:**
Ensure that everything is working by running the test suite.

```bash
poetry run pytest
```

## Contribution Workflow

1. **Create a New Branch:**
Create a feature branch for your contribution.

```bash
git checkout -b feature/your-feature-name
```

2. **Make Your Changes:**
Implement your changes, and ensure that your code follows the project’s coding standards and is properly tested.

3. **Write Tests:**
For any new functionality, write appropriate unit tests to ensure stability.

4. **Run Linting:**
Ensure your code passes linting checks using `flake8` or the configured linting tools.

```bash
poetry run flake8
```

5. **Commit Changes:**
Commit your changes with a meaningful commit message.

```bash
git add .
git commit -m "Add feature/fix: Description of your changes"
```

6. **Push to Your Fork:**
Push the changes to your feature branch.

```bash
git push origin feature/your-feature-name
```

7. **Submit a Pull Request:**
Open a pull request (PR) to the `main` branch of the A.D.I. repository. Provide a clear description of the changes and link any related issues.

## Code Style Guidelines

- Follow [PEP 8](https://pep8.org/) coding style guidelines.
- Ensure all code changes are covered with tests.
- Make sure your code is well-documented and easy to understand.

## Running Tests

We use `pytest` for testing. To run the test suite:

```bash
poetry run pytest
```

## Code Owners

The current code owner of this repository is **@aditya30051993**. For major contributions or significant changes, please reach out to the code owner for approval or guidance.

## Reporting Bugs or Requesting Features

If you find any bugs or want to request a feature, please check if an issue already exists in the GitHub Issues section. If not, feel free to open a new issue with relevant details.

## Code of Conduct

Please note that we expect contributors to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md).
