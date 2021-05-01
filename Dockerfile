FROM scratch
WORKDIR /app
COPY requirements.txt requirements.txt
COPY *.py ./
COPY package_manager/*.py package_manager/
COPY tests/*.py tests/
