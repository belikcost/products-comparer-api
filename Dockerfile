FROM snakepacker/python:all as builder

RUN python3.9 -m venv /usr/share/python3/app
RUN /usr/share/python3/app/bin/pip install -U pip
ADD . /tmp
RUN /usr/share/python3/app/bin/pip install -U '/tmp'
RUN find-libdeps /usr/share/python3/app > /usr/share/python3/app/pkgdeps.txt

FROM snakepacker/python:3.9 as api
COPY --from=builder /usr/share/python3/app /usr/share/python3/app
RUN cat /usr/share/python3/app/pkgdeps.txt | xargs apt-install
RUN ln -snf /usr/share/python3/app/bin/comparer-* /usr/local/bin/

CMD ["sh", "-c", "comparer-db revision --autogenerate; comparer-db upgrade head; comparer-api"]