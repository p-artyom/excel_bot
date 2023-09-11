run:
	python excel_bot.py

style:
	black -S -l 79 .
	isort .
	flake8 .
