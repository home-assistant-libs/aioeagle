from setuptools import setup


long_description = open("README.md").read()

setup(
    name="aioeagle",
    version="1.1.0",
    license="Apache License 2.0",
    url="https://github.com/home-assistant-libs/aioeagle",
    author="Paulus Schoutsen",
    author_email="paulus@paulusschoutsen.nl",
    description="Python module to talk to Rainforest EAGLE-200.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["aioeagle"],
    zip_safe=True,
    platforms="any",
    install_requires=list(val.strip() for val in open("requirements.txt")),
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
