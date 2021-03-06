output_index:
	python script/hs300.py
	python script/sh50.py
	python script/zz500.py

requirements:
	pip freeze > requirements.txt

install_requirements:
	pip install -r requirements.txt

debug:
	@uvicorn src.main:app --reload

run:
	@uvicorn src.main:app