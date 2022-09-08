lint:
	poetry run isort --check --diff --line-length 120 .
	poetry run black --check --diff redis_rate_limiter tests
	poetry run mypy redis_rate_limiter
	poetry run pylint redis_rate_limiter
	poetry run flake8

fix_black:
	poetry run black redis_rate_limiter tests

fix_isort:
	poetry run isort --line-length 120 .

test:
	poetry run pytest --hypothesis-show-statistics