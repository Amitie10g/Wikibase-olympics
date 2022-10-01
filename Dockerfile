FROM amitie10g/pywikibot

RUN pip install luadata

COPY olympics.py /code
