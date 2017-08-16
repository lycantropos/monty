## Running tests
Plain
```bash
python3 setup.py test
```

Inside `Docker` container
```bash
docker-compose -f docker-compose.tests.yml up
```
or with remote debugger
```bash
./set-dockerhost.sh docker-compose -f docker-compose.tests.yml up
```
