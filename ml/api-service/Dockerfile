FROM python:3.7
MAINTAINER Idar Senkir 'isenkir@yandex.com'
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5000
ENTRYPOINT [ "python" ]
CMD [ "run.py" ]