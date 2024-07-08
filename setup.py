from setuptools import setup, find_packages
import json


with open('metadata.json', encoding='utf-8') as fp:
    metadata = json.load(fp)


setup(
    name="lexibank_girardprototakanan",
    description=metadata["title"],
    license=metadata.get("license", ""),
    packages=find_packages(where="."),
    url=metadata.get("url", ""),
    py_modules=["lexibank_girardprototakanan"],
    include_package_data=True,
    zip_safe=False,
    entry_points={"lexibank.dataset": ["girardprototakanan=lexibank_girardprototakanan:Dataset"]},
    install_requires=["pylexibank>=3.0.0", "pyedictor"],
    extras_require={"test": ["pytest-cldf"]},
)