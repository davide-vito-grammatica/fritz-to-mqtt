from setuptools import setup, find_packages

setup(
    name='poc_fritzbox',
    version='0.1.0',
    author='Davide Vito Grammatica',
    author_email='davide.grammatica@sisal.it',
    description='A poc project to interact with FritzBox routers',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'requests',
        'hashlib'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)