FROM python:3.9-slim-buster

COPY . /opt/tracktor
WORKDIR /opt/tracktor
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 80
CMD ["python", "-m uvicorn", "hazel:app", "--host 0.0.0.0", "--port 80"]