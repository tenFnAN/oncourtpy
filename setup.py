# Import required functions
from setuptools import setup, find_packages

# Call setup function
setup(
    author="Paul",
    description="OnCourt Tennis Database Helper Functions",
    name="oncourtpy",
    packages=find_packages( ),
    install_requires=['numpy>=1.22', 'pandas>=1.5', 'pyodbc>=5.1.0'],
    python_requires='>=3.9',
    version="0.1.0",
)

