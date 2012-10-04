from distutils.core import setup

setup(
    name='iconmaker',
    version='1.0.0',
    author='Yev Chillen',
    author_email='yev.chillen@iconfinder.com',
    packages=['iconfinder', 'iconfinder.test'],
    scripts=[],
    url='',
    license='LICENSE.txt',
    description='Icon conversion utility',
    long_description=open('README.txt').read(),
    install_requires=[
    ],
)
