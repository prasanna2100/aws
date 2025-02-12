import boto3
import json

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    s3 = boto3.client('s3')
    
    # DynamoDB tables
    prescription_table = dynamodb.Table('Prescription')
    history_table = dynamodb.Table('Prescription_History')
    
    # Check Load Status
    pres_status = prescription_table.get_item(Key={'TableID': 'status'})['Item']['LoadStatus']
    hist_status = history_table.get_item(Key={'TableID': 'status'})['Item']['LoadStatus']
    
    if pres_status == 'COMPLETED' and hist_status == 'COMPLETED':
        # Simulate Export to S3
        s3.put_object(Bucket='my-bucket', Key='exports/prescription_data.parquet', Body=b'data')
        s3.put_object(Bucket='my-bucket', Key='exports/prescription_history.parquet', Body=b'data')
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Data exported to S3 successfully.'})
        }
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Tables not ready for export.'})
        }
