# Module 2: Encrypt the EBS

Now that your pipeline is built.  As a developer, you uploaded the zip files to s3, you committed code into the pipeline.  In this module, this example shows what a developer would experience when code does not comply with security requirements.  In this particular case, there is a security requirement that EBS volumes must be encrypted.

## First Pipeline Error

**Click on "Release Change".**

It looks like the pipeline has failed at the "Static Code Analysis" stage.

![FirstPipelineError](./images/02-firstpipelineerror.png)

1.  Click on the "Details" link and take a look at the error.  Based on the error message, what needs to be changed?
2.  Click on the "i" next to CFNParsing.

![CFNParsing](./images/02-CFNParsingInfo.png)

3.  Note the location and file this is referencing.
4.  Locate the file, resources.json and open it with your favorite editor.  (Certain editors such as Windows notepad or Mac TextEditor may not work when editing json files)
5.  Find the issue in the file and change it the value.
6.  Rezip the directory with the modified resources.json. The name of the zip file is important and must match the original name.  The pipeline is looking for that filename specifically.  If Lambda takes a while to execute, look at the logs.  
7.  Upload and overwrite the existing zip file in: “{CloudformationStackName}-artifactstorebucket-{randomstring}
8.  Go back to your CodePipeline screen and watch the stages go through processing again.  If you fixed the code correctly, it should go through to the next stage.
9.  Re-enable the transition you disabled earlier.
9. When it gets to the ApproveTestStack stage, click on the Review button and then approve the deployment. (Normally you would get an email asking for manual approval, but for the purposes of this lab, do not wait). Everything should then carry on until you have a pipeline full of stages which have succeeded.

![ApprovalStage](./images/02-ApprovalStage.png)

(Optional) Feel free to click on some **Details** icons to look into what happened at each stage in more detail.  CFNParsing is a lambda function is a script which does various checks for security compliance.

