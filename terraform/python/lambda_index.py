#------------------------------------------------------------------------------
# written by: Lawrence McDaniel
#             https://lawrencemcdaniel.com/
#
# date:       sep-2023
#
# usage:      AWS Lambda to process jpeg image files uploaded to S3.
#             - run image file against index_faces() to generate a faceprint
#             - persist the faceprint to DynamoDB
#
#             Detects faces in the input image and adds them to the specified collection.
#             Amazon Rekognition doesn’t save the actual faces that are detected.
#             Instead, the underlying detection algorithm first detects the faces
#             in the input image. For each face, the algorithm extracts facial
#             features into a feature vector, and stores it in the backend database.
#             Amazon Rekognition uses feature vectors when it performs face match
#             and search operations using the SearchFaces and SearchFacesByImage operations.
#
#             - To get the number of faces in a collection, call DescribeCollection.
#
#             - If you provide the optional ExternalImageId for the input image you provided,
#               Amazon Rekognition associates this ID with all faces that it detects.
#               When you call the ListFaces operation, the response returns the external ID.
#
#             - The input image is passed either as base64-encoded image bytes,
#               or as a reference to an image in an Amazon S3 bucket.
#
# OFFICIAL DOCUMENTATION:
#             https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rekognition/client/index_faces.html
#------------------------------------------------------------------------------
import os
import json
from decimal import Decimal
from urllib.parse import unquote_plus
import logging
import boto3

COLLECTION_ID = os.environ["COLLECTION_ID"]
TABLE_ID = os.environ["TABLE_ID"]
MAX_FACES = int(os.getenv("MAX_FACES_COUNT", "10"))
FACE_DETECT_ATTRIBUTES = os.getenv("FACE_DETECT_ATTRIBUTES", "DEFAULT")
QUALITY_FILTER = os.getenv("QUALITY_FILTER", "AUTO")
DEBUG_MODE = os.getenv("DEBUG_MODE", 'False').lower() in ('true', '1', 't')

s3_client = boto3.resource('s3')

dynamodb_client = boto3.resource('dynamodb')
dynamodb_table = dynamodb_client.Table(TABLE_ID)

rekognition_client = boto3.client('rekognition')
rekognition_collection = rekognition_client.describe_collection(CollectionId=COLLECTION_ID)

urllib3_logger = logging.getLogger('urllib3')
urllib3_logger.setLevel(logging.CRITICAL)

def lambda_handler(event, context):
    # basic sanity checks
    # ---------------------------
    if not "Records" in event:
        print('WARNING: Records object not found. Nothing to do. Exiting.')
        return {'statusCode': 500, 'data': None}

    records = event["Records"]
    if records[0]["eventSource"] != "aws:s3":
        print('ERROR: lambda_index() is intended to be called from aws:s3, but was invoked by {service}'.format(
            service=records[0]["eventSource"]
        ))
        return {'statusCode': 401, 'data': None}

    if records[0]["eventName"] != "ObjectCreated:Put":
        print('WARNING: lambda_index() is intended to be called for ObjectCreated:Put event, but was invoked by {event}'.format(
            event=records[0]["eventName"]
        ))

    # all good. process the event
    # ---------------------------
    s3_bucket_name = records[0]['s3']['bucket']['name']
    for record in records:
        key = unquote_plus(record['s3']['object']['key'], encoding='utf-8')
        try:
            s3_object = s3_client.Object(s3_bucket_name, key)
            object_metadata = {key.replace("x-amz-meta-", ""): s3_object.metadata[key] for key in s3_object.metadata.keys()}

            if DEBUG_MODE:
                print("record: {var}".format(var=json.dumps(record, indent = 4)))
                print("key={key}, s3_object={s3_object}, object_metadata={object_metadata}".format(
                    s3_object=s3_object,
                    key=key,
                    object_metadata=object_metadata
                    ))

            # analyze our newly uploaded image.
            faces = rekognition_client.index_faces(
                CollectionId=COLLECTION_ID,
                Image={
                    'S3Object': {
                                'Bucket': s3_bucket_name,
                                'Name': key
                                }
                },
                ExternalImageId=key,
                DetectionAttributes=[FACE_DETECT_ATTRIBUTES],
                MaxFaces=MAX_FACES,
                QualityFilter=QUALITY_FILTER
            )
            metadata = {key.replace("x-amz-meta-", ""): object_metadata[key] for key in object_metadata.keys()}
            #----------------------------------------------------------------------
            # return structure: doc/rekognition_index_faces.json
            #----------------------------------------------------------------------
            for face in faces["FaceRecords"]:
                face = face["Face"]
                face["bucket"] = s3_bucket_name
                face["key"] = key
                face["metadata"] = metadata
                face = json.loads(json.dumps(face), parse_float=Decimal)
                dynamodb_table.put_item(Item=face)

        except rekognition_client.exceptions.InvalidS3ObjectException:
            print("ERROR: InvalidS3ObjectException")
            return {'statusCode': 406, 'data': None}
        except rekognition_client.exceptions.InvalidParameterException:
            # If no faces are detected in the input image, SearchFacesByImage returns an InvalidParameterException error
            return {'statusCode': 200, 'data': None}
        except rekognition_client.exceptions.ImageTooLargeException:
            print("ERROR: ImageTooLargeException")
            return {'statusCode': 406, 'data': None}
        except rekognition_client.exceptions.AccessDeniedException:
            print("ERROR: AccessDeniedException")
            return {'statusCode': 403, 'data': None}
        except rekognition_client.exceptions.InternalServerError:
            print("ERROR: InternalServerError")
            return {'statusCode': 500, 'data': None}
        except rekognition_client.exceptions.ThrottlingException:
            print("ERROR: ThrottlingException")
            return {'statusCode': 401, 'data': None}
        except rekognition_client.exceptions.ProvisionedThroughputExceededException:
            print("ERROR: ProvisionedThroughputExceededException")
            return {'statusCode': 401, 'data': None}
        except rekognition_client.exceptions.ResourceNotFoundException:
            print("ERROR: ResourceNotFoundException")
            return {'statusCode': 404, 'data': None}
        except rekognition_client.exceptions.InvalidImageFormatException:
            print("ERROR: InvalidImageFormatException")
            return {'statusCode': 406, 'data': None}
        except rekognition_client.exceptions.ServiceQuotaExceededException:
            print("ERROR: ServiceQuotaExceededException")
            return {'statusCode': 401, 'data': None}
        except Exception as e:
            raise e
