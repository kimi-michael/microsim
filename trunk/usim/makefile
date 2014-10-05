docs:
	~mkimyaga/work_area/projects/dfxBuilder3.3/external_tools/epydoc-3.0.1/scripts/epydoc \
	-v --html -o docs --graph=all \
	*.py datastructures/*.py interfaces/*.py model/*.py simulation_core/*.py ./tests/*.py
clean:
	find . -name '*.pyc' -exec rm {} \;
	rm -rf ./docs



