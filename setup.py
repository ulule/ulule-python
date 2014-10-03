from setuptools import setup

import os.path

setup(
    name='ulule-python',
    version='0.1',
    author='Damien Cirotteau',
    author_email='dcirotteau@ctrl-x.fr',
    description='A Python API library for the Ulule crowdfunding platform.',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    license='MIT',
    keywords='ulule crowdfunding api',
    url='https://github.com/ulule/ulule-python',
    py_modules=['ulule'],
    install_requires=['requests >= 0.13.2', ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet :: WWW/HTTP',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ]
)
