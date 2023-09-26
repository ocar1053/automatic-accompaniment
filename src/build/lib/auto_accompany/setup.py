from setuptools import setup, find_packages

setup(
    name='auto_accompany',
    version='0.1',
    description='auto accompany package',
    packages=find_packages(),
    install_requires=[
        'AutoTune==0.0.3',
        'basic_pitch==0.2.4',
        'numpy==1.23.5',
        'PyAudio==0.2.13',
        'scipy==1.11.1',
        'setuptools==58.1.0',
        'sounddevice==0.4.6',
    ],
    classifiers=[
        "Programming Language :: Python :: 3.9.13"
    ]
)
