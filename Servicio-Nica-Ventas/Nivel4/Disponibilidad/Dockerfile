FROM python
COPY app /app
RUN pip install -r /app/requirements.txt
WORKDIR app
CMD ["python", "app.py"]
EXPOSE 5000
