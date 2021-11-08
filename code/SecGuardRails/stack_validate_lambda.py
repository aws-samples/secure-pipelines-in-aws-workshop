"""Summary
Attributes:
    AWS_CIS_BENCHMARK_VERSION (str): Description
    CONFIG_RULE (bool): Description
    CONTROL_1_1_DAYS (int): Description
    REGIONS (list): Description
    SCRIPT_OUTPUT_JSON (bool): Description
"""

from __future__ import print_function
import json
import csv
import time
import sys
import re
import tempfile
from datetime import datetime
import boto3
import botocore
import traceback
import zipfile

# Would you like to print the results as JSON to output?
SCRIPT_OUTPUT_JSON = True
code_pipeline = boto3.client('codepipeline')
EC2_CLIENT = boto3.client('ec2')
cf = boto3.client('cloudformation')


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


def stack_exists(stack):
    """Check if a stack exists or not

    Args:
        stack: The stack to check

    Returns:
        True or False depending on whether the stack exists

    Raises:
        Any exceptions raised .describe_stacks() besides that
        the stack doesn't exist.

    """
    try:
        cf.describe_stacks(StackName=stack)
        return True
    except botocore.exceptions.ClientError as e:
        if "does not exist" in e.response['Error']['Message']:
            return False
        else:
            raise e


def delete_stack(stack):
    """CloudFormation stack deletion

    Args:
        stack: The stack to be created

    Throws:
        Exception: Any exception thrown by .create_stack()
    """
    cf.delete_stack(StackName=stack)


# --- Security Groups ---
# 4.1 Ensure no security groups allow ingress from 0.0.0.0/0 to port 22 (Scored)
def control_4_1_ensure_ssh_not_open_to_world(regions, stackName):
    """Summary

    Returns:
        TYPE: Description
    """
    result = True
    failReason = ""
    offenders = []
    control = "4.1"
    description = "Ensure that security groups allow ingress from approved CIDR range to port 22"
    scored = True
    for n in regions:
        client = boto3.client('ec2', region_name=n)
        response = client.describe_security_groups(
            Filters=[{'Name': 'tag:aws:cloudformation:stack-name', 'Values': [stackName]}])
        for m in response['SecurityGroups']:
            if "1.2.3.4/32" not in str(m['IpPermissions']):
                for o in m['IpPermissions']:
                    try:
                        if int(o['FromPort']) <= 22 <= int(o['ToPort']):
                            result = False
                            failReason = "Found Security Group with port 22 open to the wrong source IP range. Allowed IP is: 1.2.3.4/32"
                            offenders.append(str(m['GroupId']))
                    except:
                        if str(o['IpProtocol']) == "-1":
                            result = False
                            failReason = "Found Security Group with port 22 open to the wrong source IP range. Allowed IP is: 1.2.3.4/32"
                            offenders.append(str(n) + " : " + str(m['GroupId']))
    return {'Result': result, 'failReason': failReason, 'Offenders': offenders, 'ScoredControl': scored,
            'Description': description, 'ControlId': control}

# --- S3 Access control ---
# 4.2 Ensure S3 bucket is not publicly accessible
def control_4_2_no_global_s3(stackName):
    """Summary
    Returns:
        TYPE: Description
    """

    # Getting the s3 bucket name first from cloudformation
    cfn = boto3.client('cloudformation')
    cfnResourceBucketInfo = cfn.describe_stack_resource(StackName=stackName,LogicalResourceId='S3Bucket')
    s3BucketName = cfnResourceBucketInfo['StackResourceDetail']['PhysicalResourceId']

    hasPassed = True
    failReason = ""
    offenders = []
    control = "4.2"
    description = "Ensure that there are no S3 elements exposed to the public"
    scored = True
    client = boto3.client('s3')

    # First check bucket policy
    try:
        response = client.get_bucket_policy(Bucket=s3BucketName)
        policyJson = json.loads(response['Policy'])
        for statement in policyJson['Statement']:
            print(statement)
            if (statement['Principal'] and ('*' in statement['Principal'])) and (statement['Effect'] and ('Allow' in statement['Effect'])) and (statement['Action'] and ('*' in statement['Action'])):
                hasPassed = False
                failReason = 'Bucket [' + s3BucketName + '] has Allow policy for everyone.'
                offenders.append(s3BucketName)
    except botocore.exceptions.ClientError as exp:
        if 'NoSuchBucketPolicy' in str(exp):
            # no policy is fine
            hasPassed = True

    if hasPassed:
        # check secondary ACL properties
        try:
            aclResponse = client.get_bucket_acl(Bucket=s3BucketName)
            for aGrant in aclResponse['Grants']:
                # contains definitions for all users then it should be invalid
                if (aGrant['Grantee']['Type'] == 'Group') and (aGrant['Grantee']['URI']) and ('groups/global/AllUsers' in aGrant['Grantee']['URI']):
                    print ('Found information about Global All users. This is not permitted')
                    hasPassed = False
                    offenders.append(s3BucketName)
                    failReason = s3BucketName + " contains ACL specifications for All Users. Update S3 AccessControl property"
        except botocore.exceptions.ClientError as expAcl:
            print('problems extracting ACL information')
            hasPassed = False
            offenders.append(s3BucketName)
            failReason = s3BucketName + " cannot read ACL information. Please check permissions on this lambda script"

    return {'Result': hasPassed, 'failReason': failReason, 'Offenders': offenders, 'ScoredControl': scored,
            'Description': description, 'ControlId': control}

def get_regions():
    region_response = EC2_CLIENT.describe_regions()
    regions = [region['RegionName'] for region in region_response['Regions']]
    return regions

def json_output(controlResult):
    """Summary

    Args:
        controlResult (TYPE): Description

    Returns:
        TYPE: Description
    """
    inner = dict()
    outer = dict()
    for m in range(len(controlResult)):
        inner = dict()
        for n in range(len(controlResult[m])):
            x = int(controlResult[m][n]['ControlId'].split('.')[1])
            inner[x] = controlResult[m][n]
        y = controlResult[m][0]['ControlId'].split('.')[0]
        outer[y] = inner
    print("JSON output:")
    print("-------------------------------------------------------")
    print(json.dumps(outer, sort_keys=True, indent=4, separators=(',', ': ')))
    print("-------------------------------------------------------")
    print("\n")
    print("Summary:")
    print(shortAnnotation(controlResult))
    print("\n")
    return 0


def shortAnnotation(controlResult):
    """Summary

    Args:
        controlResult (TYPE): Description

    Returns:
        TYPE: Description
    """
    annotation = []
    longAnnotation = False
    for m, _ in enumerate(controlResult):
        for n in range(len(controlResult[m])):
            if controlResult[m][n]['Result'] is False:
                if len(str(annotation)) < 220:
                    annotation.append(controlResult[m][n]['ControlId'])
                else:
                    longAnnotation = True
    if longAnnotation:
        annotation.append("etc")
        return "{\"Failed\":" + json.dumps(annotation) + "}"
    else:
        return "{\"Failed\":" + json.dumps(annotation) + "}"


def lambda_handler(event, context):
    """Summary

    Args:
        event (TYPE): Description
        context (TYPE): Description

    Returns:
        TYPE: Description
    """
    # Run all control validations.
    # The control object is a dictionary with the value
    # result : Boolean - True/False
    # failReason : String - Failure description
    # scored : Boolean - True/False
    # Check if the script is initiade from AWS Config Rules
    # Print the entire event for tracking
    print("Received event: " + json.dumps(event, indent=2))
    # Extract the Job ID
    job_id = event['CodePipeline.job']['id']
    # Globally used resources
    region_list = get_regions()
    stackName = event['CodePipeline.job']['data']['actionConfiguration']['configuration']['UserParameters']
    print("stackName: " + stackName)

    # Run individual controls.
    # Comment out unwanted controls
    control4 = []
    control_4_1_result = control_4_1_ensure_ssh_not_open_to_world(region_list, stackName)
    print('control_4_1_result: ' + str(control_4_1_result['Result']))
    control4.append(control_4_1_result)

    # Running 4.2 control for s3 protection
    control_4_2_result = control_4_2_no_global_s3(stackName)
    print('control_4_2_result: ' + str(control_4_2_result['Result']))
    control4.append(control_4_2_result)

    # Join results
    controls = []
    controls.append(control4)

    # Build JSON structure for console output if enabled
    if SCRIPT_OUTPUT_JSON:
        json_output(controls)

    # iterate through controls for error checks
    for control in controls:
        for controlspec in control:
            if controlspec['Result'] is False:
                print("\n")
                if stack_exists(stackName):
                    delete_stack(stackName)
                put_job_failure(job_id, controlspec['failReason'])
                return

    # found nothing and is good to go
    print("\n")
    put_job_success(job_id, 'Job succesful, minimal or no risk detected.')
