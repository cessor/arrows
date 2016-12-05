FROM alpine:latest
MAINTAINER Johannes Hofmeister <docker@spam.cessor.de>

# To Build:
# docker build -t cessor/arrows -f Dockerfile .

# To Run:
# docker run --name arrows -d -p 8000:8000 --link mongodb:mongodb cessor/arrows

RUN apk add --update bash curl g++ python3 python3-dev && \
    rm -rf /var/cache/apk/*

RUN curl https://bootstrap.pypa.io/get-pip.py > get-pip.py
RUN python3 get-pip.py
RUN pip3 install tornado
RUN pip3 install motor
RUN pip3 install xlsxwriter

ADD ./src /var/arrows

RUN python3 -c "import random,string; print('cookie_secret=\'%s\'' % ''.join([random.choice(string.ascii_letters+string.digits) for _ in range(32)]))" >> /var/arrows/config/docker.cfg

ENV TORNADO_ENV=docker
CMD python3 /var/arrows/serve-fast.py
