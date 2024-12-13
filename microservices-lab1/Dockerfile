FROM python:3.9

EXPOSE 80

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./templates /code/templates
COPY ./app /code/app

CMD ["fastapi", "run", "app/main.py", "--port", "80"]
