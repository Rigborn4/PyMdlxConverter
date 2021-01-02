from setuptools import setup, find_packages


def read_file(filename):
    with open(filename, 'r+') as f:
        return f.read()


setup(
    name="PyMdlxConverter",
    packages=find_packages(),
    version="1.0.0",
    description="An mdl-mdx converter",
    long_description=read_file("README.md"),
    author="Rigborn",
    author_email="rigborn4@gmail.com",
    url="https://github.com/Rigborn/PyMdlxConverter",
    py_modules=['PyMdlxConverter'],
    python_requires=">=3.6",
)