ifndef TEST_PATTERN
override TEST_PATTERN=''
endif


init:
	python -m pip install -r requirements.txt

test:
	clear
	pytest -vv -s -k $(TEST_PATTERN)

.PHONY: init test