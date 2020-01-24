import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='escaperoom_clues',
    version='0.1a1',
    license='GPL-3',
    author='Antonin Rousset',
    description='Display clues and chronometer in an escaperoom',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/AntoninRousset/escaperoom-display',
    scripts=['escaperoom_clues'],
    include_package_data=True,
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
        'PyQt5>=5.12.2'
    ],
    entry_points={
        'console_scripts': [
            'escaperoom_clues=escaperoom_clues.__main__:main'
        ]
    }
)
