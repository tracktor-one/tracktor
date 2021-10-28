FROM python:3.9-buster

RUN set -x ; addgroup --gid 1000 tracktor ; adduser --uid 1000 --ingroup tracktor tracktor && exit 0 ; exit 1
USER tracktor
COPY --chown=tracktor:tracktor requirements.txt /
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=tracktor:tracktor . /opt/tracktor
WORKDIR /opt/tracktor
EXPOSE 80
CMD ["/opt/tracktor/scripts/entrypoint.sh"]