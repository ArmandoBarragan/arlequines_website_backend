import uuid
import boto3
import stripe
import json
from datetime import datetime
from pydantic import BaseModel


stripe.api_key = os.environ['STRIPE_SECRET_KEY']
dynamodb = boto3.resource('dynamodb', endpoint_url=os.getenv("ENDPOINT_URL", None))
ses = boto3.client('ses')
table_reservations = dynamodb.Table("Reservations")
table_presentations = dynamodb.Table('Presentations')


class ReservationRequest(BaseModel):
    presentation_id: int
    name: str
    email: str
    token: str  # Stripe token


def make_reservation(event, context):
    data = ReservationRequest(**json.loads(event['body']))

    # Retrieve presentation for pricing
    presentation = table_presentations.get_item(Key={'id': data.presentation_id}).get('Item')
    if not presentation:
        return {"statusCode": 404, "body": "Presentation not found"}

    try:        
        payment_intent = stripe.PaymentIntent.create(
            amount=presentation['cost'],
            currency='mxn',
            source=data.token,
            description=f"Reservation for {data.presentation_id}"
        )

        confirmation_code = str(uuid.uuid4())[:8]
        table_reservations.put_item(Item={
            'id': str(uuid.uuid4()),
            'presentation_id': data.presentation_id,
            'name': data.name,
            'email': data.email,
            'confirmation_code': confirmation_code,
            'timestamp': datetime.utcnow().isoformat()
        })

        # Send confirmation email
        ses.send_email(
            Source=os.environ['SES_EMAIL_FROM'],
            Destination={'ToAddresses': [data.email]},
            Message={
                'Subject': {'Data': 'Reservation Confirmation'},
                'Body': {
                    'Text': {
                        'Data': f"Thanks {data.name}! Your reservation code is {confirmation_code}."
                    }
                }
            }
        )

        return {"statusCode": 200, "body": json.dumps({"message": "Reservation successful"})}

    except Exception as e:
        return {"statusCode": 500, "body": str(e)}
