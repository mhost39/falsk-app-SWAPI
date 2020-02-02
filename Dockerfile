FROM python:3.6

WORKDIR /app
COPY . /app

RUN pip3 install flask
RUN pip3 install requests
ENTRYPOINT ["python3"]
CMD ["app.py"]
