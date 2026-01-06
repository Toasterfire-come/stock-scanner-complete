SHELL := /bin/bash

.PHONY: help install install-frontend install-backend build test test-frontend test-backend e2e security-backend security-frontend

help:
	@echo "Targets:"
	@echo "  make install         Install backend + frontend deps"
	@echo "  make test            Run backend + frontend tests"
	@echo "  make e2e             Run Playwright E2E tests (frontend)"
	@echo "  make build           Build frontend"
	@echo "  make security-frontend  Run frontend yarn audit (allowlisted)"
	@echo "  make security-backend   Run backend bandit (best-effort)"
	@echo ""
	@echo "For full setup docs, see docs/INSTALL.md"

install: install-backend install-frontend

install-backend:
	@test -d backend/venv || python3 -m venv backend/venv
	@backend/venv/bin/python -m pip install --upgrade pip
	@backend/venv/bin/pip install -r backend/requirements.txt

install-frontend:
	@yarn --cwd frontend install

build:
	@yarn --cwd frontend build

test: test-backend test-frontend

test-backend:
	@cd backend && DJANGO_SETTINGS_MODULE=stockscanner_django.settings_ci ./venv/bin/python manage.py test

test-frontend:
	@CI=true yarn --cwd frontend test

e2e:
	@yarn --cwd frontend test:e2e

security-frontend:
	@yarn --cwd frontend security:audit

security-backend:
	@backend/venv/bin/python -m pip install --upgrade bandit >/dev/null 2>&1 || true
	@backend/venv/bin/python -m bandit -q -r backend || true

