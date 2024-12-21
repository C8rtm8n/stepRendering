from setuptools import setup, find_packages

setup(
    name='steprendering',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'streamlit',
        'pythonocc-core',
    ],
    entry_points={
        'console_scripts': [
            'steprendering=main:run_app',
        ],
    },
)
