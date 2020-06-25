FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app/
EXPOSE 8000
#CMD python boot.py
CMD ["python", "boot.py"]
