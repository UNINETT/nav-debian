FROM debian:buster

RUN  apt-get -y update && \
     apt-get install -y \
       pbuilder \
       vim \
       cdbs \
       autoconf \
       automake \
       quilt \
       reportbug \
       dh-systemd \
       git-buildpackage \
       libpq-dev \
       libjpeg-dev \
       libz-dev \
       libldap2-dev \
       libsasl2-dev \
       python3-dev \
       python-all \
       python3-all \
       libsnmp30 \
     && \
     apt-get clean

RUN  apt-get -y update && \
     apt-get install -y \
         dh-virtualenv \
         dh-python \
         python3-setuptools

ENV  HOME /home
ENV  QUILT_PATCHES debian/patches
ENV  QUILT_NO_DIFF_INDEX 1
ENV  QUILT_NO_DIFF_TIMESTAMPS 1
ENV  QUILT_REFRESH_ARGS -p ab

CMD  /bin/bash
