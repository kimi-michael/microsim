SRC_FILES = $(wildcard  ./*.py ./tests/*.py )

docs: $(SRC_FILES)
	~mkimyaga/work_area/projects/dfxBuilder3.3/external_tools/epydoc-3.0.1/scripts/epydoc \
	-v --html -o docs --graph=all \
	*.py tests/*.py
clean:
	find . -name '*.pyc' -exec rm {} \;
	rm -rf ./docs



