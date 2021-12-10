from setuptools import setup,find_packages

setup(name='taskminal',
      version='0.5',
      description='A CLI tasklist / time tracker.',
      url='https://github.com/JustADataConstruct/Taskminal',
      author='JustADataConstruct',
      license='MIT',
      entry_points = {
          'console_scripts':['taskminal=taskminal.main:main']
      },
      packages = find_packages(),
      zip_safe=False)
