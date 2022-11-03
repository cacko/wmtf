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
        "appdir==0.3.5",
        "appdirs==1.4.4",
        "arrow==1.2.3",
        "async-timeout==4.0.2",
        "beautifulsoup4==4.11.1",
        "cachable==0.3.30",
        "commonmark==0.9.1",
        "corethread==0.1.3",
        "dataclasses-json==0.5.7",
        "deprecated==1.2.13",
        "marshmallow==3.18.0",
        "marshmallow-enum==1.5.1",
        "nanoid==2.0.0",
        "pillow==9.2.0",
        "prompt-toolkit==3.0.31",
        "pyfiglet==0.8.post1",
        "pygments==2.13.0",
        "python-dateutil==2.8.2",
        "pytz-deprecation-shim==0.1.0.post0",
        "questionary==1.10.0",
        "random-user-agent==1.0.1",
        "redis==4.3.4",
        "rich==12.6.0",
        "six==1.16.0",
        "soupsieve==2.3.2.post1",
        "textual==0.3.0",
        "typing-inspect==0.8.0",
        "tzdata==2022.6",
        "tzlocal==4.2",
        "wcwidth==0.2.5",
        "wrapt==1.14.1",
    ],
    setup_requires=["wheel"],
    python_requires=">=3.10",
    packages=find_packages(include=["wmtf", "wmtf.*"]),
    entry_points="""
        [console_scripts]
        wmtf=wmtf.cli:cli
    """,
)
