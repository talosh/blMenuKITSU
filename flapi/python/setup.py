import setuptools

with open("README.md","r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="flapi",
    version="5.3.17711",
    author="FilmLight Ltd.",
    author_email="baselight-support@filmlight.ltd.uk",
    description="FilmLight API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://www.filmlight.ltd.uk/",
    packages=setuptools.find_packages(),
    install_requires=["websocket-client>=0.48"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
)

