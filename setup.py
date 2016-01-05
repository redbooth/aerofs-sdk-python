import setuptools

# If you want a package (something with an __init__.py) to wind up installed,
# you need to list it here.
packages = [
    "aerofs",
    "aerofs.api"
]

setuptools.setup(
    name='aerofs',
    version='0.1.3',
    description='aerofs',
    author='Matt Pillar',
    author_email='matt@aerofs.com',
    url='https://github.com/mpillar/aerofs-sdk-python',
    packages=packages,
    install_requires=['requests']
)
