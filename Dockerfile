FROM python:3.12-alpine

RUN pip install poetry

RUN poetry config virtualenvs.create false

WORKDIR /code

COPY pyproject.toml poetry.lock* ./


RUN poetry install --no-interaction --no-root

COPY . .

EXPOSE 8000

CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
