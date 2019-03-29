from setuptools import setup, find_packages


GENERIC_REQ = [
]

TESTS_REQ = [
    'pytest-html==1.19.0',
    'pytest-cov==2.6.0',
    'pytest==3.8.2',
]

CI_REQ = [
    'tox',
    'twine',
]

setup(
    name="dockerma",
    url="https://bitbucket.org/mortenlj/dockerma",
    use_scm_version=True,
    packages=find_packages(exclude=("tests",)),
    zip_safe=False,
    install_requires=GENERIC_REQ,
    setup_requires=['pytest-runner', 'wheel', 'setuptools_scm'],
    extras_require={
        "dev": TESTS_REQ + CI_REQ,
        "ci": CI_REQ,
    },
    tests_require=TESTS_REQ,
    entry_points={"console_scripts": ['dockerma=dockerma:main']},
    include_package_data=True,
)
