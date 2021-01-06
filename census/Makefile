ifndef TEST_PATTERN
override TEST_PATTERN=''
endif

ifdef VERBOSE
override VERBOSE_FLAG = -vv
endif

TEST_BASE = pytest $(VERBOSE_FLAG) -k $(TEST_PATTERN)

init:
	python -m pip install -r requirements.txt

test:
	clear
	$(TEST_BASE) -m "not integration"

test-integration:
	clear
	$(TEST_BASE) -m integration

test-coverage:
	clear
	pytest --cov-report term-missing:skip-covered --cov=census tests/

clean_pycache:
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

.PHONY: init test test-integration test-coverage clean_pycache