from setuptools import setup, find_packages

setup(
    name="Gasho Torrent",
    version="1.0",
    packages=find_packages(),
    install_requires=['PyQt5>=5.6', 'libtorrent>=1.1.0'],
    author='Christopher Mitov',
    author_email='christopher95@abv.bg',
    description='Simple and lightweight torrent client.',
    license='GPL',
    keywords='torrent gasho client')
