FROM python:3.9-buster

RUN set -x ; addgroup --gid 1000 tracktor ; adduser --uid 1000 --ingroup tracktor tracktor && exit 0 ; exit 1
COPY . /opt/tracktor
WORKDIR /opt/tracktor
RUN chmod +x /opt/tracktor/scripts/entrypoint.sh \
    && chown -R tracktor:tracktor /opt/tracktor \
    && pip install --no-cache-dir -r requirements.txt
USER tracktor
EXPOSE 80
CMD ["/opt/tracktor/scripts/entrypoint.sh"]