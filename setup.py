import sys
from pathlib import Path

import semver
from setuptools import find_packages, setup
from setuptools.dist import Distribution as _Distribution

__name__ = "wmtf"
vp = Path(__file__).parent / "version.txt"
__version__ = semver.VersionInfo.parse(vp.read_text().strip())

def version():
    if len(sys.argv) > 1 and sys.argv[1] == "bdist_wheel":
        nv = f"{__version__.bump_patch()}"
        vp.write_text(f'{nv}')
        return nv
    return f"{__version__}"


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
        "appdirs>=1.4.4",
        "beautifulsoup4>=4.11.1",
        "corethread>=0.1.3",
        "corestring>=0.1.4",
        "pillow>=9.2.0",
        "prompt-toolkit>=3.0.31",
        "pyfiglet>=0.8.post1",
        "pygments>=2.13.0",
        "python-dateutil>=2.8.2",
        "pytz-deprecation-shim>=0.1.0.post0",
        "questionary>=1.10.0",
        "textual>=0.4.0",
        "tzlocal>=4.2",
        "click>=8.1.3",
        "colorama>=0.4.5",
        "jira==3.4.1",
        "peewee>=3.15.3",
        "pydantic==1.10.2",
        "pyyaml==6.0",
        "requests>=2.28.1",
        "requests-oauthlib>=1.3.1",
        "requests-toolbelt>=0.10.0",
        "structlog>=22.1.0",
        "tabulate>=0.9.0",
        "pandas>=1.5.1",
        "html5lib>=1.1",
        "python-crontab>=2.6.0",
        "random-user-agent>=1.0.1",
        "progressor>=1.0.14",
        "urlextract>=1.7.1",
        "arrow>=1.2.3"
        
    ],
    setup_requires=["wheel"],
    python_requires=">=3.10",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={"wmtf.resources": ["*"]},
    entry_points="""
        [console_scripts]
        wmtf=wmtf.cli:run
    """,
)
