# Module 7: Cleanup

This last module helps with cleaning up the lab environment.  This only applies if you are running this in your own account.

## Cleanup
In order to prevent charges to your account we recommend cleaning up the infrastructure that was created. If you plan to keep things running so you can examine the workshop a bit more please remember to do the cleanup when you are done. It is very easy to leave things running in an AWS account, forget about it, and then accrue charges. 

!!! info "If you are using this in an instructor led session, with the AWS Event Engine you do not need to run the cleanup steps"

!!! info "If you are running this in your own account. You will need to manually delete some resources before you delete the CloudFormation stacks so please do the following steps in order."


1.	Delete s3 buckets.
	* Go to <a href="https://s3.console.aws.amazon.com/s3/home?region=us-west-2#" target="_blank">Amazon S3</a> console.
    * Go into the s3 bucket you created in module 1 and delete all of the contents.
    * After the bucket is empty, delete the bucket.
    * Look for *artifactstorebucket* and delete all of the contents.  You will have to click the "Show" button to show all versions of files.  The versions of files also have to be deleted before the bucket can be deleted.
    * After the bucket is empty, delete the bucket.

2.  Delete the Cloudformation stack.
	* Go to <a href="https://us-west-2.console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks?filteringText=&filteringStatus=active&viewNested=true&hideStacks=false" target="_blank">AWS Cloudformation</a> console.
    * Look for the stack deployed in module 1 and delete the stack.

3.	Delete Lambdas.
	* Go to the <a href="https://us-west-2.console.aws.amazon.com/lambda/home?region=us-west-2#/functions" target="_blank">AWS Lambda</a> console.
	* Delete the lambda functions you created.


## Finished!

Congratulations on completing this workshop! This is the workshop's permanent home, so feel free to revisit as often as you'd like.



##  Continuing On

The workshop is intended to give you an idea of how to start your own Security

