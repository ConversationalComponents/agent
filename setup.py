
from setuptools import setup
from setuptools import find_packages

long_description = '''
Puppet is a high-level toolkit for building chatbots using conversational components.
Try puppet if you want to make your chatbot modular using composable components.
'''

setup(name='coco-puppet',
      version='0.0.5',
      description='Modular composable chatbot development',
      long_description=long_description,
      author='Chen Buskilla',
      author_email='chen@buskilla.com',
      url='https://github.com/chenb67/puppet',
      license='GPLv3',
      install_requires=['marshmallow>=3.0.0',
                        'requests',
                        'coco-sdk>=0.0.2'
      ],
      package_data={
          '': ["*.json"]
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
