FROM python:3.8

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt 


COPY . .

CMD ["gunicorn", "foodest_backend.wsgi:application", "--bind", "0:8000", "--reload"]