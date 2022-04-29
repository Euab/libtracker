from setuptools import setup, find_packages


setup(
    name="libtracker",
    version='1.0',
    description=(
        "Python script and library to track the GPS position of devices and "
        "derive device attributes."
    ),
    packages=find_packages(include=["libtracker", "libtracker.*"]),
    install_requires=(
        "pyicloud",
        "requests"
    ),
    author="Euan Mills",
    author_email="euab.mills@gmail.com"
)
