from setuptools import setup

with open('ReadMe.md') as f:
    readme = f.read()

setup(
    name='code_engine',
    version='0.0.1',
    description='A python package that automatically generates production-ready python code using ML',
    long_description=readme,
    license="MIT",
    author='Jack Weissenberger',
    author_email='jack.weissenberger@gmail.com',
    url='https://github.com/jweissenberger/code-engine',
    packages='code_engine',
    install_requires=[
        'transformers==4.21.0',
        'torch'
    ]
)