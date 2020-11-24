FROM python:3.7-alpine

COPY requirements.txt /
RUN pip install flask requests

RUN mkdir -p /usr/src/app
ADD ./app.py /usr/src/app/app.py

WORKDIR /usr/src/app
EXPOSE 3123
ENV FLASK_APP /usr/src/app/app.py
CMD [ "python", "-m" , "flask", "run", "--port", "3123", "--host=0.0.0.0"]
