# Makefile

.PHONY: all build clean run

all: build

build:
	docker build -t llamacpp-exporter:latest .

clean:
	rm -f llamacpp-exporter.tar.gz

run:
	docker run -it --rm \
		-p 8001:8001 \
		-e LLAMACPP_BASE_URL="http://host.docker.internal:8000" \
		-e SERVER_PORT="8001" \
		llamacpp-exporter:latest

package:
	docker save llamacpp-exporter:latest | gzip > llamacpp-exporter.tar.gz