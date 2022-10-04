FROM python:3.7-slim
RUN mkdir /app
WORKDIR /app
ADD . /app
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
CMD ["python", "api.py"]
EXPOSE 5000