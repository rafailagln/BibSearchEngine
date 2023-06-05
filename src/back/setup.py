from setuptools import setup, find_packages

setup(
    name='Back BibSearch Engine',
    version='1.0.0',
    description='Your project description',
    author='Your Name',
    author_email='your-email@example.com',
    url='https://github.com/your-github/your-project',
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
        'pymongo',
        'nltk',
        'uvicorn',
        'fastapi'
    ]
)
