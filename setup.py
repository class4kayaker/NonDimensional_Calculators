"""
A utility to package subsets of large ASPECT PVD files to visualize elsewhere
without access to the original filesystem.
"""

from setuptools import find_packages, setup

package = 'sci_parameter_utils'
version = '0.2.0'
dependencies = [
    'click',
    'pyyaml',
    'sympy'
]
test_deps = [
    'pytest'
]
setup_deps = [
    'pytest-runner'
]

setup(
    name=package,
    version=version,
    package_dir={'': 'src'},
    packages=find_packages('src', exclude=['tests']),
    setup_requires=setup_deps,
    install_requires=dependencies,
    tests_require=test_deps,
    entry_points={
        'console_scripts': [
            'sci_parameter_utils = sci_parameter_utils.cli:cli_main'
        ]
    }
)
