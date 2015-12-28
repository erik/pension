from setuptools import setup


setup(
    name='pension',
    version='0.1.0',
    description='Alert when ec2 instances are scheduled for retirement',
    author='Erik Price',
    url='https://github.com/erik/pension',
    packages=['pension'],
    entry_points = {
        'console_scripts': [
            'pension = pension.cli:main',
        ],
    },
    license='MIT',
    install_requires=open('requirements.txt').readlines()
)
