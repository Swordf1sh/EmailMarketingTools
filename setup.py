from setuptools import setup, find_packages

setup(
    name='EmailMarketingTools',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        # list your package dependencies
    ],
    # Additional metadata about your package
    author='Jasper',
    author_email='your.email@example.com',
    description='A short description of your package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/your_package_name',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
