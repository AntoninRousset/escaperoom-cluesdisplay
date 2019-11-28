import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='escaperoom-display',
    version='0.1a1',
    license='GPL-3',
    author='Antonin Rousset',
    description='Display informations in an escaperoom',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/pypa/sampleproject',
    scripts=['escaperoom-display.py'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='>=3.6, <3.7',
    install_requires=[
        'PyQt5>=5.12.2',
        'aiohttp>=3.6.1'
    ]
)
