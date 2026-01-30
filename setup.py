from setuptools import setup, find_packages

setup(
    name='lin_age_calculator',
    version='0.1.0',

    packages=find_packages(),
    include_package_data=True,
    package_data={
        'calculator': ['models/*.csv'],
    },

    install_requires=[
        'numpy',
        'pandas',
    ],
)
