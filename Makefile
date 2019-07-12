.PHONY: docker-build docker-run

docker-build:
	@docker build -t devsecops-ignore .

docker-run:
	@bash -c 'source .env && docker run --rm -it -e GITHUB_PERSONAL_TOKEN=$${GITHUB_PERSONAL_TOKEN} devsecops-ignore'
