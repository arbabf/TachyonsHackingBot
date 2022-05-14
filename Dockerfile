# based on debian buster 
FROM python:3.9 

WORKDIR /hackbot 

COPY requirements.txt requirements.txt 
COPY src/hackbot/  . 

RUN pip3 install -r requirements.txt 

USER root 

ENTRYPOINT ["python3"]

CMD ["/hackbot/hackbot.py"]



