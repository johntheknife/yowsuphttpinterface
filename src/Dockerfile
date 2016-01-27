From frolvlad/alpine-python2
RUN apk --update add gcc python-dev musl-dev libffi
ADD . /src
RUN pip install -r /src/requirements.txt

ENTRYPOINT ["python","/src/yowsupflask.py"]