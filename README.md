docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

python manage.py graph_models -a --output schema.png


## Data

How the corpus files are imported and what leaves for the server:
see [data/README.md](data/README.md).
