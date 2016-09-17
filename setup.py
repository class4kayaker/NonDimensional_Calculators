"""
A utility to package subsets of large ASPECT PVD files to visualize elsewhere
without access to the original filesystem.
"""

import sys
from setuptools import find_packages, setup

needs_pytest = {'pytest', 'test'}.intersection(sys.argv)
pytest_runner = ['pytest_runner'] if needs_pytest else []

package = 'sci_parameter_utils'
version = '0.2.0'
dependencies = [
    'click',
    'pyyaml',
    'sympy',
]
setup_deps = [
] + pytest_runner
test_deps = [
    'pytest',
]

setup(
    name=package,
    version=version,
    package_dir={'': 'src'},
    packages=find_packages('src', exclude=['tests']),
    install_requires=dependencies,
    setup_requires=setup_deps,
    tests_require=test_deps,
    entry_points={
        'console_scripts': [
            'sci_parameter_utils = sci_parameter_utils.cli:cli_main'
        ]
    },
)
