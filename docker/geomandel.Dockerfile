FROM python:3.9.0-buster

# Build geomandel from sources
RUN apt-get update && apt-get install -y libsfml-dev cmake

RUN git clone https://github.com/crapp/geomandel.git /golem/geomandel
RUN mkdir /golem/geomandel/build
WORKDIR /golem/geomandel/build
RUN cmake -DCMAKE_BUILD_TYPE=Release ../
RUN make && make install

WORKDIR /golem/work
# Copy helper scripts
COPY ./scripts/mandel.py /golem/scripts/mandel.py
COPY ./scripts/golem-mandel.py /golem/scripts/golem-mandel.py

CMD ["python", "/golem/scripts/golem-mandel.py"]

VOLUME /golem/work /golem/output /golem/resource
