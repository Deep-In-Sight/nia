from setuptools import setup

__version__ = "1.0"

setup(
    name="nia22",
    version=__version__,
    author="DeepInsight",
    #packages=find_packages(),
    author_email="hschoi@dinsight.ai",
    url="",
    description="NIA2022 Tool box",
    long_description="",
    zip_safe=False,
    force=True # force recompile the shared library. 
)
