from setuptools import setup, find_packages

setup(
    name="pyshepherd",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "mido>=1.2.10",
        "websockets>=10.0",
    ],
    extras_require={
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0", 
            "pytest-mock>=3.10.0",
        ]
    },
    python_requires=">=3.8",
)