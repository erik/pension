from setuptools import setup


setup(
    name='pension',
    version='0.0.4',
    description='Alert when ec2 instances are scheduled for retirement',
    author='Erik Price',
    url='https://github.com/erik/pension',
    packages=['pension'],
    entry_points={
        'console_scripts': [
            'pension = pension.cli:main',
        ],
    },
    license='MIT',
    install_requires=[
        'boto3==1.2.3',
        'click==6.2',
        'toml==0.9.1',
        'requests==2.9.1'
    ]
)
