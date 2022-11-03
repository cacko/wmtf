import sys
from pathlib import Path

import semver
from setuptools import find_packages, setup
from setuptools.dist import Distribution as _Distribution

from wmtf import __name__


def version():
    if len(sys.argv) > 1 and sys.argv[1] == "bdist_wheel":
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
        "blinker==1.5",
        "brotlipy==0.7.0",
        "bzip2==1.0.8",
        "ca-certificates==2022.9.24",
        "certifi==2022.9.24",
        "cffi==1.15.1",
        "charset-normalizer==2.1.1",
        "click==8.1.3",
        "colorama==0.4.5",
        "cryptography==38.0.2",
        "defusedxml==0.7.1",
        "flake8==5.0.4",
        "idna==3.4",
        "importlib-metadata==4.11.4",
        "jaraco.classes==3.2.2",
        "jira==3.4.1",
        "keyring==23.9.3",
        "libffi==3.4.2",
        "libsqlite==3.39.4",
        "libzlib==1.2.13",
        "mccabe==0.7.0",
        "more-itertools==8.14.0",
        "mypy_extensions==0.4.3",
        "ncurses==6.3",
        "oauthlib==3.2.1",
        "openssl==1.1.1q",
        "packaging==21.3",
        "pathspec==0.10.1",
        "peewee==3.15.3",
        "platformdirs==2.5.2",
        "pycodestyle==2.9.1",
        "pycparser==2.21",
        "pydantic==1.10.2",
        "pyflakes==2.5.0",
        "pyjwt==2.5.0",
        "pyopenssl==22.1.0",
        "pyparsing==3.0.9",
        "pysocks==1.7.1",
        "python==3.10.6",
        "python_abi==3.10",
        "pyyaml==6.0",
        "readline==8.1.2",
        "requests==2.28.1",
        "requests-oauthlib==1.3.1",
        "requests-toolbelt==0.10.0",
        "semver==2.13.0",
        "setuptools==65.4.1",
        "sqlite==3.39.4",
        "structlog==22.1.0",
        "tk==8.6.12",
        "tomli==2.0.1",
        "typing-extensions==4.4.0",
        "urllib3==1.26.11",
        "wheel==0.37.1",
        "xz==5.2.6",
        "yaml==0.2.5",
        "zipp==3.9.0",
    ],
    setup_requires=["wheel"],
    python_requires=">=3.10",
    packages=find_packages(include=["wmtf", "wmtf.*"]),
    entry_points="""
        [console_scripts]
        wmtf=wmtf.cli:cli
    """,
)
