POETRY=poetry
MANAGE=src/manage.py
ENV_FILE=config.env

# Load environment variables from config.env
ifneq (,$(wildcard $(ENV_FILE)))
    include $(ENV_FILE)
    export $(shell sed 's/=.*//' $(ENV_FILE))
endif

.PHONY: help install runserver migrate make-migration dump-data create-superuser db-shell shell shell-plus show-urls test lint collect-static make-messages compile-messages

help: ## Show this help
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	$(POETRY) install

runserver: ## Run the Django development server
	$(POETRY) run $(MANAGE) runserver

migrate: ## Apply database migrations
	$(POETRY) run $(MANAGE) migrate

make-migration: ## Create a migration
	$(POETRY) run $(MANAGE) makemigrations

dump-data: ## Dump data
	$(POETRY) run $(MANAGE) dumpdata

create-superuser: ## Create a superuser
	$(POETRY) run $(MANAGE) createsuperuser

db-shell: ## Run the Django database shell
	$(POETRY) run $(MANAGE) dbshell

shell-plus: ## Run the Django shell plus with IPython
	$(POETRY) run $(MANAGE) shell_plus --print-sql --ipython

shell: ## Run the Django shell
	$(POETRY) run $(MANAGE) shell

show-urls: ## Show all urls
	$(POETRY) run $(MANAGE) show_urls

test: ## Run tests
	$(POETRY) run $(MANAGE) test

lint: ## Run linters
	$(POETRY) run flake8 src/

collect-static: ## Collect static files
	$(POETRY) run $(MANAGE) collectstatic

make-messages: ## Create messages
	cd ./src && $(POETRY) run $(MANAGE) makemessages -l fa

compile-messages: ## Compile messages
	cd ./src && $(POETRY) run $(MANAGE) compilemessages

## docker compose
# TODO: add docker compose commands
