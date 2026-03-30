FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt /tmp/model_finetuning_requirements.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install -r /tmp/model_finetuning_requirements.txt

COPY . /app/model_finetuning

WORKDIR /app

CMD ["bash"]
