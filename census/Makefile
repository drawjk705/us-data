ifndef TEST_PATTERN
override TEST_PATTERN=''
endif


init:
	python -m pip install -r requirements.txt

test:
	clear
	pytest -vv -k $(TEST_PATTERN)

test-coverage:
	clear
	pytest --cov-report term-missing:skip-covered --cov=census tests/

clean_pycache:
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

.PHONY: init test clean_pycache