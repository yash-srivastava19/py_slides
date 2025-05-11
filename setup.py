from setuptools import setup, find_packages

setup(
    name="py_slides",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[],  # Add dependencies here
)

"""
from setuptools import setup, find_packages

setup(
    name="termslides",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "markdown",
        "blessed",
        "pygments",
        "rich",
    ],
    entry_points={
        "console_scripts": [
            "termslides=termslides:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A terminal-based markdown slide presentation tool",
    keywords="presentation, markdown, terminal, slides",
    python_requires=">=3.7",
)
"""