FROM python:3.7

#RUN apk update && apk upgrade

RUN /usr/local/bin/python -m pip install --default-timeout=100 --upgrade pip
RUN pip install --default-timeout=100 flask requests
RUN pip install --default-timeout=100 apscheduler

RUN mkdir -p /usr/src/app
ADD ./app.py /usr/src/app/app.py

WORKDIR /usr/src/app
EXPOSE 3123
ENV FLASK_APP /usr/src/app/app.py
ENV ENV prod

CMD [ "python", "-m" , "flask", "run", "--port", "3123", "--host=0.0.0.0"]
