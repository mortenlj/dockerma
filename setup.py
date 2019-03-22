from datetime import datetime
from subprocess import check_output, CalledProcessError
from warnings import warn

from setuptools import setup, find_packages


def version():
    date_string = datetime.now().strftime("1.%Y%m%d.%H%M%S")
    try:
        git_sha = check_output(["git", "describe", "--always", "--dirty=dirty", "--match=NOTHING"]).strip().decode()
        return "{}+{}".format(date_string, git_sha)
    except (CalledProcessError, OSError) as e:
        warn("Error calling git: {}".format(e))
    return date_string


GENERIC_REQ = [
]

TESTS_REQ = [
    'pytest-html==1.19.0',
    'pytest-cov==2.6.0',
    'pytest==3.8.2',
]

CI_REQ = [
    'tox',
    'tox-travis',
]

setup(
    name="dockerma",
    url="https://bitbucket.org/mortenlj/dockerma",
    version=version(),
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
