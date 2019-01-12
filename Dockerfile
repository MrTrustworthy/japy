FROM python:3.7

COPY japy/ japy/
COPY requirements.txt requirements.txt
COPY wsgi.py wsgi.py

EXPOSE 3000

RUN python -m pip install -r requirements.txt

CMD ["gunicorn", "--bind", "0.0.0.0:3000", "wsgi"]