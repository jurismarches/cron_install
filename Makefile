tests:
	python -m unittest tests

quality:
	black --check --line-length=100 .
	flake8 . --max-line-length=100

distribute:
	[ -d dist ] || mkdir dist
	[ -z $(ls dist/) ] || rm dist/*
	python3 setup.py sdist
	twine check dist/*
	twine upload -u jurismarches -s dist/*
