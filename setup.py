import setuptools
# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
setuptools.setup(
    name='remote_run_everything',
    version='0.02',
    description='远程上传、调试、下载任何语言',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Wang Qi',
    author_email='wangmarkqi@gmail.com',
    url='https://github.com/wangmarkqi/remote_run_everything',
    packages=setuptools.find_packages(),
    keywords=['remote', 'debug', 'development tool'],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',

)


'''
# 上传source 包
python setup.py sdist
twine upload dist/*

'''
