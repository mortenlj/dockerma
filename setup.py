import os

from setuptools import setup, find_packages

GENERIC_REQ = [
    "appdirs==1.4.3",
    "six",
]

TESTS_REQ = [
    'pytest-html==1.19.0',
    'pytest-cov==2.6.0',
    'pytest==3.8.2',
    'mock==3.0.5',
]

CI_REQ = [
    'tox',
    'tox-gh-actions',
    'publish',
]


def _generate_description():
    description = [_read("README.rst")]
    changelog_file = os.getenv("CHANGELOG_FILE")
    if changelog_file:
        description.append(_read(changelog_file))
    return "\n".join(description)


def _get_license_name():
    license = _read("LICENSE")
    lines = license.splitlines()
    return lines[0].strip()


def _read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()


setup(
    name="dockerma",
    use_scm_version=True,
    packages=find_packages(exclude=("tests",)),
    zip_safe=True,
    install_requires=GENERIC_REQ,
    setup_requires=['pytest-runner', 'wheel', 'setuptools_scm'],
    extras_require={
        "dev": TESTS_REQ + CI_REQ,
        "ci": CI_REQ,
    },
    tests_require=TESTS_REQ,
    entry_points={"console_scripts": ['dockerma=dockerma:main']},
    include_package_data=True,
    # Metadata
    author="Morten Lied Johansen",
    author_email="mortenjo@ifi.uio.no",
    description="DockerMA facilitates building multi-arch containers with minimal fuss",
    long_description=_generate_description(),
    license=_get_license_name(),
    url="https://github.com/mortenlj/dockerma",
    project_urls={
        "Source": "https://github.com/mortenlj/dockerma/src",
        "Tracker": "https://github.com/mortenlj/dockerma/issues"
    },
    keywords="docker",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development",
        "Topic :: Software Development :: Build Tools",
        "Topic :: System :: Software Distribution",
        "Topic :: Utilities",
    ],
)
