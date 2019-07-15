.PHONY: run lint docker-build docker-run

dep:
	@pip3 install --user -r requirements.txt -r requirements-dev.txt

run:
	@python3 src/main.py

lint:
	@pylama src/

docker-build:
	@docker build -t devsecops-ignore .

docker-run:
	@docker run --rm -it --env-file .env devsecops-ignore
