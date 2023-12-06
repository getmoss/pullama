import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pullama",
    version = "0.0.1",
    author = "Paulo Suzart",
    author_email = "paulo.suzart@getmoss.com",
    description = ("A git diff Summarizer backed by LLM on Ollama"),
    license = "MIT",
    keywords = "llm ai devxp",
    url = "https://github.com/getmoss/pullama",
    packages=['pullama', 'pullama.diffchain'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: Experimentation",
        "Topic :: AI",
        "License :: MIT License",
    ],
)