from setuptools import setup, find_packages

setup(
    name="polydim",
    version="26.155.0",
    description="POLYDIM EINSOF — High-Dimensional Tensor Cognition Engine (SOTA)",
    author="Ariel & Antigravity Swarm",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.24.0",
    ],
    entry_points={
        "console_scripts": [
            "polydim=polydim.cli:main",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.14",
    ],
)
