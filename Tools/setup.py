from setuptools import setup


setup(
    name="datasetsml-tools",
    version="0.1.0",
    description="Reusable Tools package for DatasetsML notebooks",
    packages=["Tools", "Tools.DatasetTools"],
    package_dir={"Tools": ".", "Tools.DatasetTools": "DatasetTools"},
    include_package_data=True,
    install_requires=[
        "nbformat>=4.2.0",
        "scikit-learn>=1.5",
    ],
)
