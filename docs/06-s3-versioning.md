<!--
Testing the lambda function created in the previous module.
--> 
# Module 6:  Configuring S3 Security

Many organizations utilize s3 extensively.  It is important that the s3 buckets are configured to the organization's requirements to ensure data stored safely.


1.	Now that you have added a lambda function to enforce enablement of S3 Versioning Configuration.  Release the change to start the pipeline.

!!! question "What is S3 Versioning?  How can it help you secure data?"



2.	Add the appropriate configuration.
    1.	Edit resource.json and add the appropriate lines.
    2.	Rezip the “codepipe-AWS-devsecops.zip” (the exact name is important)
    3.	Upload the zip to s3.
3.	Come back to the DevSecOps pipeline and watch it through the stages again.


!!! info "Hint: <a href="https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html" target="_blank">https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html</a href>"

!!! question "Are there other s3 configurations you would want to enforce?  Are there other AWS native ways to enforce some of those controls?"


