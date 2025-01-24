#!/bin/bash

# Check if python is installed
if ! command -v python3 &> /dev/null; then
  echo "Python is not installed. Installing Python 3.12..."
  # Install Python 3.12 using Homebrew (if available)
  if command -v brew &> /dev/null; then
    brew install python@3.12
  else
    echo "Homebrew is not installed. Please install Python 3.12 manually."
    exit 1
  fi
fi

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
if [[ ! $(echo "${python_version}" | grep -E '^3\.[1][2-9]') ]]; then
  echo "Python version is not 3.12 or higher. Please install Python 3.12."
  exit 1
fi
#!/bin/bash

# Check for xlsm-trans-env virtual environment
if ! python3 -m venv --help &> /dev/null; then
  echo "Error: python -m venv command not found. Please ensure Python 3 is installed."
  exit 1
fi

if [[ ! -d "xlsm-trans-env" ]]; then
  echo "Creating virtual environment xlsm-trans-env..."
  python3 -m venv xlsm-trans-env
else
  echo "Virtual environment xlsm-trans-env already exists."
fi

# Activate virtual environment
source xlsm-trans-env/bin/activate

# Install libraries from requirements.txt
echo "Installing libraries from requirements.txt..."
pip3 install -r requirements.txt

# Run Streamlit app
echo "Running Streamlit app..."
python3 ./src/run.py

# Deactivate virtual environment (optional)
# deactivate