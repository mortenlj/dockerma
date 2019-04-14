import os
import re
import subprocess

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
ISSUE_NUMBER = re.compile(r"#(\d+)")


def _generate_changelog():
    output = subprocess.check_output(["hg", "parent", "--template", "{latesttag}\t{latesttagdistance}"],
                                     universal_newlines=True)
    tag, distance = output.split("\t")
    limit = int(distance) - 1
    if limit > 0:
        header = "Changes since {}".format(tag)
        changelog = [header, "-" * (len(header)), ""]
        links = {}
        output = subprocess.check_output(["hg", "log", "-l", str(limit), "--template", "{node|short}\t{desc}\n"],
                                         universal_newlines=True)
        for line in output.splitlines():
            node, desc = line.split("\t", maxsplit=1)
            links[node] = ".. _{node}: https://bitbucket.org/mortenlj/dockerma/commits/{node}".format(node=node)
            for match in ISSUE_NUMBER.finditer(desc):
                issue_number = match.group(1)
                links[issue_number] = ".. _#{num}: https://bitbucket.org/mortenlj/dockerma/issues/{num}".format(
                    num=issue_number)
            desc = ISSUE_NUMBER.sub(r"`#\1`_", desc)
            changelog.append("* `{node}`_: {desc}".format(node=node, desc=desc))
        changelog.append("")
        changelog.extend(links.values())
        return "\n".join(changelog)
    return ""


def _generate_description():
    description = [_read("README.rst"), _generate_changelog()]
    return "\n".join(description)


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
    url="https://bitbucket.org/mortenlj/dockerma",
    keywords="docker",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
