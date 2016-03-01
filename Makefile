.PHONY: clean-py clean

help:
help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "test-all - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -f *.log

lint: lint-libs lint-statsd

lint-statsd:
	flake8 netuitive-statsd

lint-libs:
	flake8 libs

coverage-html:
	coverage run --source libs setup.py test
	coverage report -m
	coverage html
	open htmlcov/index.html

coverage:
	coverage run --source libs setup.py test
	coverage report -m

test:
	python setup.py test

test-all:
	tox

dist: clean
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

# install: clean
# 	python setup.py install

# release: clean
# 	python setup.py sdist upload
# 	python setup.py bdist_wheel upload
