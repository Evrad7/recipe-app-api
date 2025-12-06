FROM python:3.11-alpine3.22

LABEL maintainer="tsoataevrad7@example.com"

ARG DEV=false

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY ./requirements.txt /tmp

COPY ./requirements.dev.txt /tmp/requirements.dev.txt

RUN python -m venv /py

RUN /py/bin/pip install --upgrade pip && \
/py/bin/pip install -r /tmp/requirements.txt && \
if [ "$DEV" = "true" ]; \
   then /py/bin/pip install -r /tmp/requirements.dev.txt; \
fi && \
rm -rf /tmp && \
adduser \ 
   --disabled-password \
   --no-create-home \
   django-user 

COPY . /app

ENV PATH="/py/bin:$PATH"

EXPOSE 8000

USER django-user

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]