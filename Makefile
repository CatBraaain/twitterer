default:
	type Makefile

clean:
	if exist dist rmdir /s /q dist
	if exist src\\twitterer.egg-info rmdir /s /q src\\twitterer.egg-info

build: clean
	python -m pip install --upgrade build
	python -m build

publish: build
	python -m pip install --upgrade twine
	twine upload dist/*
