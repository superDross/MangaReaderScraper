
build:
	docker build -t manga:latest .

run:
	docker run -v $(PWD):/app -p 4444:4444 --rm manga:latest python3 scraper/ $(ARGS)

test:
	docker run -v $(PWD):/app --rm manga:latest python3 -m pytest tests/
