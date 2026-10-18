from setuptools import setup, find_namespace_packages

setup(
    name="polydim",
    version="1.0.0.post26504",
    packages=find_namespace_packages(include=["polydim", "polydim.*"]),
    py_modules=["polydim_v26503_monolito", "polydim_triton_kernel_v26503"],
    install_requires=[
        "numpy>=1.20.0",
        "torch>=2.0.0",
    ],
    include_package_data=True,
    package_data={
        "polydim": ["Core.lean"],
    },
    description="POLYDIM EINSOF: High-Dimensional Continuous Manifold Computing",
    author="Ariel García Traba",
    license="Apache-2.0",
    python_requires=">=3.9",
)
