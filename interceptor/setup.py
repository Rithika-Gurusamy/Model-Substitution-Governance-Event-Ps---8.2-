from setuptools import setup, find_packages

setup(
    name="governance-interceptor",
    version="0.1.0",
    description="LLM Gateway Interceptor SDK for Model Substitution Governance",
    author="Model Substitution Governance Team",
    packages=find_packages(),
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
