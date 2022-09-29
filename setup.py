from setuptools import setup

__version__ = "1.0"

setup(
    name="nia22",
    version=__version__,
    author="DeepInsight",
    #package_dir={"nia22": "py"},
    packages=['nia22'],
    author_email="hschoi@dinsight.ai",
    url="",
    description="NIA2022 Tool box",
    long_description="",
    zip_safe=False,
    force=True # force recompile the shared library. 
)
