"""Installation with setuptools or pip."""
from setuptools import setup, find_packages
import os
import ast


#  Use following command in Project path: python3 setup.py install --user
# Then use "from package import Class" in code scripts to import relative code

def get_version_from_init():
    """Obtain library version from main init."""
    init_file = os.path.join(
        os.path.dirname(__file__), 'cah', '__init__.py'
    )
    with open(init_file) as fd:
        for line in fd:
            if line.startswith('__version__'):
                return ast.literal_eval(line.split('=', 1)[1].strip())


with open('README.md') as f:
    readme = f.read()

with open('COPYING') as f:
    lic = f.read()


setup(
    name='cah',
    version=get_version_from_init(),
    description='Cards-Against-Humanity: A politically unacceptable hilarious card game',
    long_description=readme,
    author='Arthur Vandenhoeke, Sofia Adorni, Viktor Weinand',
    author_email='arthur.vandenhoeke@gmail.com',
    url='https://github.com/viktorErasmusHogeschool/intelligent-interfaces',
    license=lic,
    packages=find_packages(exclude=('tests', 'docs', 'examples')),
    install_requires=[
        'pygame',
        'pandas',
        'numpy',
    ],
    package_data={'cah': []},
)
