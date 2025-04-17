from setuptools import setup, find_packages

setup(
    name="rivabrowser",
    version="1.2.2",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "urllib3",
    ],
    entry_points={
        "console_scripts": [
            "riva=riva.__main__:main",
        ],
    },
)
