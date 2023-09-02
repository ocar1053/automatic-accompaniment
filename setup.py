from setuptools import setup, find_packages

setup(
    name='auto_accompanys',
    version='0.1',
    description='auto accompany package',
    # Explicitly list the packages you want
    packages=['auto_accompany', 'data_process'],
    package_dir={'': 'src'},
    install_requires=[
        'AutoTune==0.0.3',
        'basic_pitch==0.2.4',
        'numpy==1.23.5',
        'PyAudio==0.2.13',
        'scipy==1.11.1',
        'setuptools==58.1.0',
        'sounddevice==0.4.6',
        'absl-py==1.4.0',
        'annotated-types==0.5.0',
        'anyio==3.7.1',
        'appdirs==1.4.4',
        'asttokens==2.2.1',
        'astunparse==1.6.3',
        'atomicwrites==1.4.1',
        'attrs==23.1.0',
        'audioread==3.0.0',
        'autopep8==2.0.2',
        'backcall==0.2.0',
        'cachetools==5.3.0',
        # ... 其他套件
        'webcolors==1.13',
        'websockets==11.0.3',
        'Werkzeug==2.2.3',
        'wrapt==1.15.0',
        'yarg==0.1.9',
        'zipp==3.15.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.9.13"
    ]
)
