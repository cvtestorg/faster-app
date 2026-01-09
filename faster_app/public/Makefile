# Docker 镜像仓库配置
REGISTRY := artifactory.gz.cvte.cn/gitlab-cicd/it.infrastructure/faster_app
PLATFORM := linux/amd64

# 从命令行参数获取版本号
# 支持两种方式：
# 1. make build VERSION=v0.0.15
# 2. make build v0.0.15 (通过 filter-out 获取位置参数)
VERSION := $(or $(VERSION),$(filter-out $@ build push help,$(MAKECMDGOALS)))

.PHONY: build push help

help:
	@echo "usage:"
	@echo "  make build VERSION=v0.0.15  - build docker image"
	@echo "  make build v0.0.15          - build docker image (simplified way)"
	@echo "  make push VERSION=v0.0.15   - push docker image to registry"
	@echo "  make push v0.0.15           - push docker image to registry (simplified way)"
	@echo ""
	@echo "examples:"
	@echo "  make build v0.0.15"
	@echo "  make push v0.0.15"

build:
	@if [ -z "$(VERSION)" ]; then \
		echo "error: please provide version, e.g. make build v0.0.15"; \
		exit 1; \
	fi
	@echo "build: $(REGISTRY):$(VERSION)"
	docker build -t $(REGISTRY):$(VERSION) --platform $(PLATFORM) .
	@echo "build done: $(REGISTRY):$(VERSION)"

push:
	@if [ -z "$(VERSION)" ]; then \
		echo "error: please provide version, e.g. make push v0.0.15"; \
		exit 1; \
	fi
	@echo "push: $(REGISTRY):$(VERSION)"
	docker push $(REGISTRY):$(VERSION)
	@echo "push done: $(REGISTRY):$(VERSION)"

# 捕获位置参数，防止 Makefile 将版本号当作 target 处理
%:
	@:
