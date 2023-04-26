import boto3
import time
from utils import load_json, get_json_from_url
from uuid import uuid4
import os


session = boto3.Session(
    aws_access_key_id=os.environ.get('AWS_ACCESS_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_KEY'),
    region_name=os.environ.get('AWS_REGION')
)


def connect_to_dynamo_table(table_name):
    """
    Connect to a DynamoDB table and return the table object
    """
    dynamodb = session.resource('dynamodb')
    table = dynamodb.Table(table_name)
    return table


transcription_table = connect_to_dynamo_table('Transcriptions')


def add_transcript(transcript_id, transcript_text, user_id):
    """
    Add a transcript to a DynamoDB table
    """
    transcription_table.put_item(
        Item={'id': transcript_id, 'transcript': transcript_text, 'user_id': user_id})


def get_transcript(transcript_id):
    """
    Get a transcript from a DynamoDB table using an id
    """
    response = transcription_table.get_item(Key={'id': transcript_id})
    transcript = response.get('Item', None)
    if transcript:
        return transcript.get('transcript')
    else:
        return None


def upload_to_s3(bucket_name, file_path, local_file_path):
    """
    Upload a file to an S3 bucket

    :param bucket_name: string
    :param file_path: string
    :param object_name: string
    :return: True if file was uploaded, else False
    """

    # Create S3 client
    s3 = session.client('s3')
    # Upload the file
    try:
        with open(local_file_path, 'rb') as file:
            response = s3.upload_fileobj(file, bucket_name, file_path)
            print(response)
    except Exception as e:
        print('Print EXception in upload_to_s3')
        print(e)
        return False

    return True


def transcribe_audio(bucket_name, file_name):
    """
    Transcribe an audio file using AWS Transcribe

    :param bucket_name: string
    :param file_name: string
    :return: Transcription result if successful, else None
    """
    # Create Transcribe client
    transcribe = session.client('transcribe')

    # Set up Transcribe job
    job_name = str(uuid4())
    job_uri = f"s3://{bucket_name}/{file_name}"
    media_format = file_name.split(".")[-1]
    language_code = "en-US"
    settings = {
        "ChannelIdentification": False,
        "ShowAlternatives": True,
        "MaxAlternatives": 2
    }

    # Start Transcribe job
    try:

        response = transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': job_uri},
            MediaFormat=media_format,
            LanguageCode=language_code,
            Settings=settings
        )
    except Exception as e:
        print('Print EXception in start_transcription_job')
        print(e)
        return None

    # Wait for Transcribe job to finish
    while True:
        status = transcribe.get_transcription_job(
            TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        time.sleep(5)
    # Get transcription result
    try:
        result_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
        response = get_json_from_url(result_uri)
        transcript = response['results']['transcripts'][0]['transcript']
    except Exception as e:
        print('Print EXception in get_object')
        print(e)
        return None
    print('Where 3')
    return transcript
