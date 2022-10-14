import sys
from pathlib import Path

import semver
from setuptools import find_packages, setup
from setuptools.dist import Distribution as _Distribution

from wmtf import __name__


def version():
    if len(sys.argv) > 1 and sys.argv[1] == "py2app":
        init = Path(__file__).parent / __name__.lower() / "version.py"
        _, v = init.read_text().split(" = ")
        cv = semver.VersionInfo.parse(v.strip('"'))
        nv = f"{cv.bump_patch()}"
        init.write_text(f'__version__ = "{nv}"')
        return nv
    from wmtf.version import __version__

    return __version__


class Distribution(_Distribution):
    def is_pure(self):
        return True


setup(
    name=__name__,
    version=version(),
    author="cacko",
    author_email="alex@cacko.net",
    distclass=Distribution,
    url=f"http://pypi.cacko.net/simple/{__name__}/",
    description="whatever",
    install_requires=[
        "colorama>=0.4.5",
        "jira>=3.4.1",
        "peewee>>=3.15.3",
        "pytermgui>=6.4.0",
        "pyyaml>=6.0",
        "sqlite>=3.39.4",
        "structlog>=22.1.0",
        "yaml>=0.2.5",
        "appdir>=0.3.5",
        "cachable>=0.3.30",
    ],
    setup_requires=["wheel"],
    python_requires=">=3.10",
    packages=find_packages(include=["w,tf", "w,tf.*"]),
    entry_points="""
        [console_scripts]
        wmtf=wmtf.cli:cli
    """,
)
