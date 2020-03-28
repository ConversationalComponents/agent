
import os
from setuptools import setup
from setuptools import find_packages

def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()

long_description = read("README.md")

setup(name='coco-puppet',
      version='0.0.8',
      description='Modular composable chatbot development',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Chen Buskilla',
      author_email='chen@buskilla.com',
      url='https://github.com/chenb67/puppet',
      license='GPLv3',
      install_requires=[
          "aioconsole",
          "coco-sdk[async]>=0.0.6"
          ],
      extras_require={
          "discord": ["discord.py"],
          "msbf": []
      },
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'Intended Audience :: Education',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.7',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ],
      packages=find_packages(),
      python_requires=">=3.7"
)
