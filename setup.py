from setuptools import setup

setup(
    name='config-woman',
    version='0.1',
    py_modules=['main'],
    install_requires=[
        'click',
        'appdirs',
        'distro',
        'pyyaml',
    ],
    entry_points='''
        [console_scripts]
        config-woman=main:cli
    ''',
)
