run: clean build up

build:
	cp -r ../../compose compose
	docker-compose -f docker-compose.local.yml build

up:
	docker-compose -f docker-compose.local.yml up

clean:
	rm -rf compose
