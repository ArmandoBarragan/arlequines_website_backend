import json
import boto3
import uuid
import os
from datetime import datetime
from pydantic import BaseModel
from typing import List


dynamodb = boto3.resource('dynamodb')
table_presentations = dynamodb.Table(
    os.getenv('PRESENTATIONS_TABLE', "ArlequinesPresentations")
)


class Presentation(BaseModel):
    presentation_id: int
    date: datetime.Date
    cost: float
    location: str
    seats_limit: int

class PresentationsRequest(BaseModel):
    presentations: List[Presentation]


def create_presentations(event, context):
    try:
        data = PresentationsRequest(**json.loads(event["body"]))
        for presentation in data.presentations:
            table_presentations.put_item(Item={
                'id': str(uuid.uuid4()),
                'play_id': presentation.play_id,
                'date': presentation.date,
                'cost': presentation.cost,
            })
    except Exception as e:
        return {"statusCode": 500, "body": str(e)}

def get_presentations_list(event, context):
    try:
        now = datetime.utcnow().isoformat()
        response = table_presentations.scan(
            FilterExpression=Attr('date').gt(now)
        )
        presentations = response.get('Items', [])
        return {
            "statusCode": 200,
            "body": json.dumps(presentations)
        }
    except Exception as e:
        return {"statusCode": 500, "body": str(e)}

def get_presentation_detail(event, context):
    try:
        presentation_id = event['pathParameters']['id']
        response = table_presentations.get_item(Key={'id': presentation_id})
        item = response.get('Item')

        if not item:
            return {"statusCode": 404, "body": "Presentation not found"}

        return {"statusCode": 200, "body": json.dumps(item)}

    except Exception as e:
        return {"statusCode": 500, "body": str(e)}

def edit_presentation(event, context):
    try:
        data = PresentationRequest(**json.loads(event['body']))

        table_presentations.update_item(
            Key={'id': data.id},
            UpdateExpression="SET #d = :d, cost = :c, limit = :l",
            ExpressionAttributeNames={"#d": "date"},
            ExpressionAttributeValues={
                ":d": data.date,
                ":c": data.cost,
                ":l": data.seats_limit,
            }
        )

        return {"statusCode": 200, "body": json.dumps({"message": "Presentation updated"})}

    except Exception as e:
        return {"statusCode": 500, "body": str(e)}
