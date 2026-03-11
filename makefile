py=.venv/bin/python
pip=.venv/bin/pip
user=guenthner
program-name=simple-oop

install_dependencies:
	python3 -m venv .venv
	$(py) -m pip install --upgrade pip
	$(pip) install build hatchling twine colorama pytest hypothesis mydefaults mypy types-colorama

test:
	$(py) -m pytest $(args)

set_user:
	cp ~/.pypirc_$(user) ~/.pypirc

build: clean version
	$(py) -m build

version:
	vinc

clean:
	mkdir dist -p
	touch dist/fuck
	rm dist/*

upload: set_user build
	$(py) -m twine upload --repository pypi dist/* $(flags)

reload: upload
	pipx upgrade $(program-name)
	pipx upgrade $(program-name)
	$(program-name) --version