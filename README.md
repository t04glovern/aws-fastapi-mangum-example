# aws-fastapi-mangum-example

## Run Locally

```bash
# Local dynamodb
docker-compose up -d

# Local api
cd api/
pip install -r requirements.txt
LOCAL_DEV=True python app.py
```

### Testing

```bash
# Create user
curl -X POST http://0.0.0.0:8080/user/ids \
     -H "Content-Type: application/json" \
     -d '{"userId": "user123", "firstname": "John", "lastname": "Doe", "age": 30}'

# List users
curl http://0.0.0.0:8080/user/ids
```

## Deploy

```bash
pip install -r requirements-dev.txt

sam build
sam validate
sam deploy
```

### Testing

```bash
# Create user
curl -X POST https://xxxxxxxxx.execute-api.ap-southeast-2.amazonaws.com/user/ids \
     -H "Content-Type: application/json" \
     -d '{"userId": "user123", "firstname": "John", "lastname": "Doe", "age": 30}'

# List users
curl https://xxxxxxxxx.execute-api.ap-southeast-2.amazonaws.com/user/ids
```
