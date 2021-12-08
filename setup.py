from setuptools import setup,find_packages

setup(name='taskminal',
      version='0.1',
      description='A CLI tasklist / time tracker.',
      url='https://github.com/JustADataConstruct/Taskminal',
      author='JustADataConstruct',
      license='MIT',
      entry_points = {
          'console_scripts':['taskminal=taskminal.taskminal:main']
      },
      packages = ['taskminal'],
      zip_safe=False)
