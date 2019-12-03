<!--
This module is designed to show how Governance and Security engineering can take requirements and automate them into a pipeline.
--> 


# Module 3: No AWS Keys Allowed!

In this module, as a Security engineer, you will add a lambda function that will look for AWS Access and Secret keys.


## Setting Lambda to Look for AWS Credentials

1.	Browse to the Lambda console, and create a new function from scratch. 
2.	Be sure to select the Python 2.7 runtime, and the module*PipelineL-<random> IAM Role.  
3.  Name the function to your choosing.  Create function.
3.	Set the Lambda time out to 1 minute.
4.	`cfn_secrets.py` is provided in the workshop.  Open this in your favorite editor.
5.  Paste the contents of `cfn_secrets.py` source editor (the one in the Lambda console), overwriting the initial placeholder function.
6.	Browse back to the CodePipeline Console, and open your DevSecOps Pipeline again. 
7.	Edit the pipeline, using the button at the top right.

![Edit-Pipeline](./images/03-Edit-Pipeline.png)

7.	Use the `Edit Stage` button for the StaticCodeAnalysis stage. 
8.	Select the Edit icon for the CFNParsing function. 
9.	Copy the contents of “User Parameters (optional)” to your paste buffer. Close the Edit action pop-up. 

![Source](./images/03-Source.png)

10.	Add a new action group.
    1.	Select “Add action group”.
    2.	Create a name for your key-scanning action, choose AWS Lambda from the Action provider drop-down. 
    3.	In “Function name”, select the name you gave your Lambda function in Step 2 above. 
    4.	TemplateSource in the “Input artifacts” drop-down.
    5.	Paste the contents of your paste buffer from above into “User Parameters (optional)”
    6.	Select Save the newly-edited pipeline. You must check the “No resource updates needed for this source action change” option on the pipeline save pop-up window. 
11.	Your new Lambda function is now integrated into your pipeline.

**Proceed to the next module to test your Lambda function.**


