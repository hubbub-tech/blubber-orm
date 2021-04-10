from setuptools import setup

setup(name='blubber_orm',
      version='0.1',
      description='Custom ORM for Hubbub DB',
      url='https://github.com/hubbub-tech/blubber-orm',
      author='Ade Balogun',
      author_email='abalogun316@gmail.com',
      license='MIT',
      packages=['funniest'],
      install_requires=[
        'psycopg2',
        'datetime',
        'pytz'
        ]
      zip_safe=False)
