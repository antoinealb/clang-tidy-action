FROM ubuntu:18.04

RUN apt-get update && apt-get install -y \
        bear \
        git \
        jq \
        python3 \
        python3-pip \
        wget \
        xz-utils

RUN pip3 install requests~=2.22.0

RUN wget "http://releases.llvm.org/9.0.0/clang+llvm-9.0.0-x86_64-linux-gnu-ubuntu-18.04.tar.xz" -O clang.tar.xz && \
    tar xf clang.tar.xz && \
    cd clang* && \
    cp -R * /usr/local

COPY analyze.py /usr/local/bin/analyze.py
COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
