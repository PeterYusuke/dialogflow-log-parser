import setuptools

with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

setuptools.setup(
    name='dialogflow_log_parser',
    version='0.0.3',
    author='Peter Yusuke',
    author_email='yyamashita1201@gmail.com',
    description='parse dialogflow log string',
    packages=setuptools.find_packages(exclude=['test', 'test.*']),
    url='https://github.com/PeterYusuke/dialogflow-log-parser',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
    ],
    install_requires=[
        'pyhocon==0.3.59'
    ],
    keywords='dialogflow parse log hocon',
    long_description=readme,
    long_description_content_type="text/markdown",
)
