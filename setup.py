from setuptools import setup,find_packages

def readme():
    with open("README.md","r") as f:
        return f.read()

setup(name='taskminal',
      version='0.5',
      description='A CLI tasklist / time tracker.',
      long_description=readme(),
      classifiers = ['Development Status :: 4 - Beta',
                     'Environment :: Console',
                     'Intended Audience :: End Users/Desktop',
                     'License :: OSI Approved :: MIT License',
                     'Programming Language :: Python :: 3.9',
                     'Topic :: Utilities'],
      keywords='sqlite time tracker to-do list',
      url='https://github.com/JustADataConstruct/Taskminal',
      author='JustADataConstruct',
      license='MIT',
      entry_points = {
          'console_scripts':['taskminal=taskminal.main:main']
      },
      packages = find_packages(),
      zip_safe=False)
