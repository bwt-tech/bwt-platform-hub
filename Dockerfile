FROM public.ecr.aws/docker/library/python:3.14
ENV TZ=America/Sao_Paulo
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata && \
    ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /bwt

COPY ./app /bwt/app
COPY ./migrations /bwt/migrations
RUN pip install --no-cache-dir -r /bwt/app/requirements.txt -U

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--log-level", "info"]
