from __future__ import print_function
from boto3.session import Session

import json
import urllib
import boto3
import zipfile
import tempfile
import botocore
import traceback
import re
import zipfile
import time

print('Loading function')
print ()
cf = boto3.client('cloudformation')
code_pipeline = boto3.client('codepipeline')

def find_artifact(artifacts, name):
    """Finds the artifact 'name' among the 'artifacts'

    Args:
        artifacts: The list of artifacts available to the function
        name: The artifact we wish to use
    Returns:
        The artifact dictionary found
    Raises:
        Exception: If no matching artifact is found

    """
    for artifact in artifacts:
        if artifact['name'] == name:
            return artifact

    raise Exception('Input artifact named "{0}" not found in event'.format(name))

def get_user_params(job_data):
    print(job_data)
    """Decodes the JSON user parameters and validates the required properties.

    Args:
        job_data: The job data structure containing the UserParameters string which should be a valid JSON structure

    Returns:
        The JSON parameters decoded as a dictionary.

    Raises:
        Exception: The JSON can't be decoded or a property is missing.

    """
    try:
        # Get the user parameters which contain the artifact and file settings
        user_parameters = job_data['actionConfiguration']['configuration']['UserParameters']
        decoded_parameters = json.loads(user_parameters)

    except Exception as e:
        # We're expecting the user parameters to be encoded as JSON
        # so we can pass multiple values. If the JSON can't be decoded
        # then fail the job with a helpful message.
        raise Exception('UserParameters could not be decoded as JSON')

    if 'input' not in decoded_parameters:
        # Validate that the artifact name is provided, otherwise fail the job
        # with a helpful message.
        raise Exception('Your UserParameters JSON must include the artifact name')

    if 'file' not in decoded_parameters:
        # Validate that the template file is provided, otherwise fail the job
        # with a helpful message.
        raise Exception('Your UserParameters JSON must include the template file name')

    if 'output' not in decoded_parameters:
        # Validate that the template file is provided, otherwise fail the job
        # with a helpful message.
        raise Exception('Your UserParameters JSON must include the output bucket')

    return decoded_parameters

def get_template(s3, artifact, file_in_zip):
    """Gets the template artifact

    Downloads the artifact from the S3 artifact store to a temporary file
    then extracts the zip and returns the file containing the CloudFormation
    template.

    Args:
        artifact: The artifact to download
        file_in_zip: The path to the file within the zip containing the template

    Returns:
        The CloudFormation template as a string

    Raises:
        Exception: Any exception thrown while downloading the artifact or unzipping it

    """
    tmp_file = tempfile.NamedTemporaryFile()
    bucket = artifact['location']['s3Location']['bucketName']
    key = artifact['location']['s3Location']['objectKey']

    with tempfile.NamedTemporaryFile() as tmp_file:
        print("Retrieving s3://" + bucket + "/" + key)
        s3.download_file(bucket, key, tmp_file.name)
        with zipfile.ZipFile(tmp_file.name, 'r') as zip:
            zip.printdir()
            return zip.read(file_in_zip)


def put_job_success(job, message):
    """Notify CodePipeline of a successful job

    Args:
        job: The CodePipeline job ID
        message: A message to be logged relating to the job status

    Raises:
        Exception: Any exception thrown by .put_job_success_result()

    """
    print('Putting job success')
    print(message)
    code_pipeline.put_job_success_result(jobId=job)

def put_job_failure(job, message):
    """Notify CodePipeline of a failed job

    Args:
        job: The CodePipeline job ID
        message: A message to be logged relating to the job status

    Raises:
        Exception: Any exception thrown by .put_job_failure_result()

    """
    print('Putting job failure')
    print(message)
    code_pipeline.put_job_failure_result(jobId=job, failureDetails={'message': message, 'type': 'JobFailed'})

def continue_job_later(job, message):
    """Notify CodePipeline of a continuing job

    This will cause CodePipeline to invoke the function again with the
    supplied continuation token.

    Args:
        job: The JobID
        message: A message to be logged relating to the job status
        continuation_token: The continuation token

    Raises:
        Exception: Any exception thrown by .put_job_success_result()

    """

    # Use the continuation token to keep track of any job execution state
    # This data will be available when a new job is scheduled to continue the current execution
    continuation_token = json.dumps({'previous_job_id': job})

    print('Putting job continuation')
    print(message)
    code_pipeline.put_job_success_result(jobId=job, continuationToken=continuation_token)

def get_user_params(job_data):
    print(job_data)
    """Decodes the JSON user parameters and validates the required properties.

    Args:
        job_data: The job data structure containing the UserParameters string which should be a valid JSON structure

    Returns:
        The JSON parameters decoded as a dictionary.

    Raises:
        Exception: The JSON can't be decoded or a property is missing.

    """
    try:
        # Get the user parameters which contain the artifact and file settings
        user_parameters = job_data['actionConfiguration']['configuration']['UserParameters']
        decoded_parameters = json.loads(user_parameters)

    except Exception as e:
        # We're expecting the user parameters to be encoded as JSON
        # so we can pass multiple values. If the JSON can't be decoded
        # then fail the job with a helpful message.
        raise Exception('UserParameters could not be decoded as JSON')

    if 'input' not in decoded_parameters:
        # Validate that the artifact name is provided, otherwise fail the job
        # with a helpful message.
        raise Exception('Your UserParameters JSON must include the artifact name')

    if 'file' not in decoded_parameters:
        # Validate that the template file is provided, otherwise fail the job
        # with a helpful message.
        raise Exception('Your UserParameters JSON must include the template file name')

    if 'output' not in decoded_parameters:
        # Validate that the template file is provided, otherwise fail the job
        # with a helpful message.
        raise Exception('Your UserParameters JSON must include the output bucket')

    return decoded_parameters

def setup_s3_client(job_data):
    """Creates an S3 client

    Uses the credentials passed in the event by CodePipeline. These
    credentials can be used to access the artifact bucket.

    Args:
        job_data: The job data structure

    Returns:
        An S3 client with the appropriate credentials

    """
    key_id = job_data['artifactCredentials']['accessKeyId']
    key_secret = job_data['artifactCredentials']['secretAccessKey']
    session_token = job_data['artifactCredentials']['sessionToken']

    session = Session(
        aws_access_key_id=key_id,
        aws_secret_access_key=key_secret,
        aws_session_token=session_token)
    return session.client('s3', config=botocore.client.Config(signature_version='s3v4'))


def evaluate_template(template, job_id):
    # Validate rules and increase risk value
    #print(template)
    risk = 0
    failedRules = []
    print("----------------")
    template = json.loads(template)

    #print(template)

    for r in template['Resources']:
        #print(template['Resources'][r])
        for s in template['Resources'][r]:
            #print(s)
            if template['Resources'][r][s] == template['Resources'][r]['Type']:
                #print(template['Resources'][r]['Type'])
                if template['Resources'][r]['Type'] == 'AWS::EC2::SecurityGroup':
                    #print(template['Resources'][r]['Properties'])
                    for sg in template['Resources'][r]['Properties']['SecurityGroupIngress']:
                        if sg == 'FromPort':
                            print(template['Resources'][r]['Properties']['SecurityGroupIngress']['FromPort'])
                            if str(template['Resources'][r]['Properties']['SecurityGroupIngress']['FromPort']) == '21':
                                risk = risk + 100
                                print("Risk value: " +str(risk))
                                failedRules.append("Found FTP port.")
                                print("killing job")
                                put_job_failure(job_id, "Found FTP port.")
                            print('Found FTP port.')
    print("----------------")

    if risk > 10:
        print("good job")
        put_job_success(job_id, 'Job succesful, minimal or no risk detected.')

    return risk, failedRules

def s3_next_step(s3, bucket, risk, failedRules, template, job_id):
    # Store data in temporary physical file
    s3Client = boto3.client('s3', config=botocore.client.Config(signature_version='s3v4'))
    tmp_file = tempfile.NamedTemporaryFile()
    tmp_zip = tempfile.NamedTemporaryFile()
    for item in template:
        tmp_file.write(item)
    tmp_file.flush()
    # Process file based on risk value
    if risk < 5:
        with zipfile.ZipFile(tmp_zip.name, 'w') as zip:
            zip.write(tmp_file.name, "valid.template.json")
            zip.close()
            s3Client.upload_file( # Add encryption support
                tmp_zip.name,
                bucket,
                'valid.template.zip')
        tmp_file.close()
        put_job_success(job_id, 'Job succesful, minimal or no risk detected.')
    elif 5 <= risk < 50:
        with zipfile.ZipFile(tmp_zip.name, 'w') as zip:
            zip.write(tmp_file.name, "flagged.template.json")
            zip.close()
            s3Client.upload_file( # Add encryption support
                tmp_zip.name,
                bucket,
                'flagged.template.zip')
        tmp_file.close()
        put_job_success(job_id, 'Job succesful, medium risk detected, manual approval needed.')
    elif risk >= 50:
        tmp_file.close()
        print("High risk file, fail pipeline")
        put_job_failure(job_id, 'Function exception: Failed filters ' + str(failedRules))
    return 0


def lambda_handler(event, context):
    """The Lambda function handler

    Validate input template for security vulnerables.  Route as appropriate based on risk assesment.

    Args:
        event: The event passed by Lambda
        context: The context passed by Lambda

    """
    try:
        # Print the entire event for tracking
        print("Received event: " + json.dumps(event, indent=2))
        print(event)
        # Extract the Job ID
        job_id = event['CodePipeline.job']['id']

        # Extract the Job Data
        job_data = event['CodePipeline.job']['data']

        # Extract the params
        user_parameters = job_data['actionConfiguration']['configuration']['UserParameters']
        decoded_parameters = json.loads(user_parameters)

        # Get the list of artifacts passed to the function
        input_artifacts = job_data['inputArtifacts']

        params = get_user_params(job_data)

        input_artifact = params['input']
        template_file = params['file']
        output_bucket = params['output']

        # Get the artifact details
        input_artifact_data = find_artifact(input_artifacts, input_artifact)

        # Get S3 client to access artifact with
        s3 = setup_s3_client(job_data)

        # Get the JSON template file out of the artifact
        template = get_template(s3, input_artifact_data, template_file)
        #print("Template: " + str(template))


        # Validate template from risk perspective. FailedRules can be used if you wish to expand the script to report failed items
        risk, failedRules = evaluate_template(template, job_id)

        # Based on risk, store the template in the correct S3 bucket for future process
        s3_next_step(s3, output_bucket, risk, failedRules, template, job_id)

    except Exception as e:
        # If any other exceptions which we didn't expect are raised
        # then fail the job and log the exception message.
        print('Function failed due to exception.')
        print(e)
        traceback.print_exc()
        put_job_failure(job_id, 'Function exception: ' + str(e))

    print('Function complete.')
    return "Complete."
