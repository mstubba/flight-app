FROM python:3.13.2
WORKDIR /app

# Najpierw same zależności: ta warstwa przebuduje się tylko po zmianie requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]