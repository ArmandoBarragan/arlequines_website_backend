import boto3
import json
import uuid
import os
from pydantic import BaseModel


dynamodb = boto3.resource('dynamodb')
table_plays = dynamodb.Table(
    os.getenv("PLAYS_TABLE", 'ArlequinesPlays')
)


class EditPlayRequest(BaseModel):
    name: str
    currently_showing: bool
    synopsis: str

class PlayRequest(BaseModel):
    name: str
    author: str
    currently_showing: bool
    synopsis: str


def create_play(event, context):
    try:
        data = PlayRequest(**json.loads(event['body']))
        play_id = str(uuid.uuid4())

        table_plays.put_item(Item={
            'id': play_id,
            'name': data.name,
            'currently_showing': data.currently_showing,
            'synopsis': data.synopsis
        })

        return {"statusCode": 200, "body": json.dumps({"message": "Play created"})}

    except Exception as e:
        return {"statusCode": 500, "body": str(e)}

def get_plays_list(event, context):
    try:
        response = table_plays.scan()
        plays = response.get("Items", [])
        return {
            "status_code": 200,
            "body": json.dumps(plays),
        }
    except Exception as e:
        return {
            "status_code": 500,
            "body": str(e),
        }

def get_play_detail(event, context):
    try:
        play_id = event['pathParameters']['id']
        response = table_presentations.get_item(Key={'id': play_id})
        item = response.get('Item')

        if not item:
            return {"statusCode": 404, "body": "Presentation not found"}

        return {"statusCode": 200, "body": json.dumps(item)}

    except Exception as e:
        return {"statusCode": 500, "body": str(e)}

def edit_play(event, context):
    try:
        data = EditPlayRequest(**json.loads(event['body']))

        table_plays.update_item(
            Key={'id': data.id},
            UpdateExpression="SET #d = :d, cost = :c",
            ExpressionAttributeNames={"#d": "date"},
            ExpressionAttributeValues={
                ":d": data.date,
                ":c": data.cost
            }
        )

        return {"statusCode": 200, "body": json.dumps({"message": "Presentation updated"})}

    except Exception as e:
        return {"statusCode": 500, "body": str(e)}
