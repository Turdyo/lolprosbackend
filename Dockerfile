FROM python
WORKDIR /app
COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt
COPY . ./
RUN python manage.py collectstatic
CMD ["gunicorn", "-w=4", "-b=0.0.0.0:8000", "lolprosbackend.wsgi:application"]