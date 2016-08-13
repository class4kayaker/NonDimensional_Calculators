"""
A utility to package subsets of large ASPECT PVD files to visualize elsewhere
without access to the original filesystem.
"""

from setuptools import find_packages, setup

package = 'sci_parameter_utils'
version = '0.1.0'
dependencies = [
    'click',
    'pyyaml',
    'sympy'
]

setup(
    name=package,
    version=version,
    packages=find_packages(exclude=['data']),
    install_requires=dependencies,
    entry_points={
        'console_scripts': [
            'print_params = sci_parameter_utils.cli:parse_nondim_params'
        ]
    }
)
