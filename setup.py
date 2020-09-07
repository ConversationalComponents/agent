import os
from setuptools import setup
from setuptools import find_packages

PYPI_PACKAGE_VERSION = os.environ.get("PYPI_PACKAGE_VERSION", "dev")


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


long_description = read("README.md")

setup(
    name="agt",
    version=PYPI_PACKAGE_VERSION,
    description="Modular composable chatbot development",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Chen Buskilla",
    author_email="chen@buskilla.com",
    url="https://github.com/ConversationalComponents/agent",
    license="GPLv3",
    entry_points="""
        [console_scripts]
        agt=agt.shell:shell_app
    """,
    install_requires=[
        "coco-sdk[async]>=0.0.8",
        "aioconsole",
        "pydantic",
        "typer",
        "pyyaml",
        "python-dotenv",
    ],
    extras_require={
        "discord": ["discord.py"],
        "msbf": ["botbuilder_core"],
        "telegram": ["aiogram"],
        "dsl": ["hy"],
        "vendor": ["sanic", "python-dotenv"],
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),
    python_requires=">=3.6",
)
