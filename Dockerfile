FROM python:3.9
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY ./requirements.txt requirements.txt
COPY libreries/num2words  libreries/num2words/
RUN cd libreries/num2words/ && pip install  ./
RUN ["pip", "freeze", " >", "requirements.txt"]
RUN ["pip", "install", "-r", "requirements.txt"]
COPY .  /app