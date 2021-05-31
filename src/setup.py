from setuptools import setup, find_packages

setup(name='blubber_orm',
      version='0.1.0',
      description='Custom ORM for Hubbub DB',
      url='https://github.com/hubbub-tech/blubber-orm',
      author='Ade Balogun',
      author_email='abalogun316@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=['psycopg2', 'datetime', 'uritools', 'pytz', 'Werkzeug']
      )

#source .env
#python3 setup.py sdist bdist_wheel
#deactivate
#python3 -m twine upload --repository testpypi dist/*
#pip3 install -i https://test.pypi.org/simple/ blubber-orm [--upgrade]
