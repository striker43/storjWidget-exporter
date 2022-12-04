FROM python:3.11-alpine

RUN pip install flask requests
RUN pip install apscheduler

RUN mkdir -p /usr/src/app
ADD ./app.py /usr/src/app/app.py

WORKDIR /usr/src/app
EXPOSE 3123
ENV FLASK_APP /usr/src/app/app.py
ENV ENV prod

CMD [ "python", "-m" , "flask", "run", "--port", "3123", "--host=0.0.0.0"]
