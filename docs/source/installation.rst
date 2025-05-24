Installation
============

1.  **Clone the repository:**
    .. code-block:: bash

       git clone <repository-url>  # Replace <repository-url> with the actual URL
       cd iechelle-project-directory # Replace with the actual directory name

2.  **Create a Python environment (recommended):**
    .. code-block:: bash

       python -m venv venv
       source venv/bin/activate  # On Windows: venv\Scripts\activate

3.  **Install dependencies:**
    This project uses Poetry for dependency management and packaging. Ensure you have Poetry installed. You can install it following the instructions on the `official Poetry website <https://python-poetry.org/docs/#installation>`_.
    Once Poetry is installed, navigate to the project root directory and run:

    .. code-block:: bash

       poetry install

    This will create a virtual environment (if one isn't active) and install all necessary dependencies.
