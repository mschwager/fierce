FROM python:slim

WORKDIR /fierce
ADD . /fierce
RUN pip3 install -r requirements.txt

ENTRYPOINT ["/usr/local/bin/python3", "/fierce/fierce/fierce.py"]
CMD ["--help"] # Displays the help message if no parameters are specified

