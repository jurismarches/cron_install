# !/usr/bin/env python
from os import path
from distutils.core import setup


dir_path = path.abspath(path.dirname(__file__))
with open(path.join(dir_path, "README.rst")) as f:
    long_description = f.read()


setup(
    name="cron-install",
    packages=[],
    py_modules=["cron_install"],
    version="0.2.0",
    description="A simple command to install a cron table.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author="Octopusmind",
    license="MIT",
    author_email="contact@octopusmind.info",
    url="https://github.com/jurismarches/cron_install",
    keywords=["cron", "template"],
    python_requires=">=3.6",
    extras_require={"quality": ["black>=19.10b0", "flake8>=3.7"], "distribute": ["wheel", "twine"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: System :: Installation/Setup",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
)
