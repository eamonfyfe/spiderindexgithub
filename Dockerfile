FROM python:3.6

RUN pip install --upgrade pip

RUN pip install scrapy

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

ADD app.py /

RUN pip install Flask==1.1.1

FROM hashicorp/terraform:light

WORKDIR /terraform

RUN ["terraform", "init"]

CMD [ "apply"]

CMD [ "python", "app.py" ]