clean:
	rm -rf env

env:
	virtualenv-2.7 env
	. env/bin/activate && pip2 install -r requirements.txt

env_test:
	. env/bin/activate && pip2 install -r requirements_test.txt

test:
	PYTHONPATH=$PYTHONPATH:src py.test-2.7 -x --strict tests
