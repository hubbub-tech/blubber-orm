from setuptools import setup, find_packages

setup(name='blubber_orm',
      version='0.4.0',
      description='Custom ORM for Hubbub DB',
      url='https://github.com/hubbub-tech/blubber-orm',
      author='Ade Balogun',
      author_email='abalogun316@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=['psycopg2', 'datetime', 'uritools', 'pytz', 'Werkzeug']
      )
