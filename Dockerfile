FROM python:3.6.8
COPY . /app
WORKDIR /app
RUN pip install pipenv
RUN pipenv install
EXPOSE 8080
CMD ["pipenv", "run", "python", "-m", "title_explorer"]