local_install:
  python3 -m pip install -e .

build:
  rm -rf __pycache__ dist build latch.egg-info
  python3 setup.py sdist bdist_wheel

publish: build
  twine upload dist/*
