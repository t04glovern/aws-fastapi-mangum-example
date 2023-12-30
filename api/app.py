import os

import boto3
from botocore.exceptions import ClientError

from pydantic import BaseModel
from typing import List
from fastapi import FastAPI, HTTPException

from mangum import Mangum

app = FastAPI()

AWS_REGION = os.environ.get('AWS_REGION', 'ap-southeast-2')
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'users')

def create_dynamodb_table(dynamodb, table_name):
    try:
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'userId',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'userId',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )
        print(f"Table {table_name} created successfully.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"Table {table_name} already exists.")
        else:
            raise

if os.environ.get('LOCAL_DEV', False):
    os.environ['AWS_ACCESS_KEY_ID'] = 'dummy'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'dummy'
    dynamodb = boto3.resource('dynamodb', endpoint_url='http://0.0.0.0:8000', region_name=AWS_REGION)
    create_dynamodb_table(dynamodb, DYNAMODB_TABLE)
else:
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)

table = dynamodb.Table(DYNAMODB_TABLE)

class User(BaseModel):
    userId: str
    firstname: str
    lastname: str
    age: int

class ErrorResponse(BaseModel):
    error: bool
    message: str

@app.post("/user/ids", response_model=User, status_code=201, responses={400: {"model": ErrorResponse}})
async def create_user(user: User):
    existing = table.get_item(Key={'userId': user.userId})
    if 'Item' in existing:
        raise HTTPException(status_code=400, detail="User already exists. Use PUT to update.")

    user_dict = user.model_dump()
    table.put_item(Item=user_dict)
    return user_dict

@app.get("/user/ids", response_model=List[User])
async def list_users():
    response = table.scan()
    items = response.get('Items', [])

    users = [User(**item) for item in items]
    return users

handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
