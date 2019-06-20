# devops

## Adobe DevOps Exercise

Out of brevity, the IAM policy used was that of a System Administrator.  These are not locked down and would be in a real-world environment.

As opposed to having the source code inline with the CloudFormation template, I have instead opted to create the Lambda Function beforehand in an S3Bucket that's also freshly created.  I could have scripted it to build the first S3 Bucket, upload the lambda function, and then run a second CloudFormation template, but opted for this way, instead.

### Dependencies
Before you get started, review the dependencies.  
`python3`  
`python3-distutils` python3 distribution utilities.  Required for `pip`/`pip3`.  
`pip3` python3 package installer.  Required for `boto3`.  
`boto3` python3 package.  Amazon's official AWS Python SDK.  
`awscli` python3 package.  Amazon's official command line API interface.  Can be installed via `pip3`, `apt`, or `yum`.

### File List

| Filename                                             | Notes                                                             |
|------------------------------------------------------|-------------------------------------------------------------------|
| `README.md`                                          | This file                                                         |
| `bin/create_cf_stack.py`                             | Handles AWSCLI creation of CloudFormation Stacks                  |
| `bin/create_stack`                                   | Wrapper for the above Python script                               |
| `bin/delete_cf_stack.py`                             | Handles AWSCLI deletion of CloudFormation Stacks                  |
| `bin/delete_stack`                                   | Wrapper for the above Python script                               |
| `bin/show_cf_stacks.py`                              | Displays Cloudformation stacks                                    |
| `bin/upload`                                         | Script that uploads lambda source to S3                           |
| `bin/upload_to_s3.py`                                | Upload an arbitrary file to an S3 bucket                          |
| `bin/lambda/lambda.zip`                              | Gets overwritten every time lambda function code gets updated     |
| `bin/lambda/s3trigger.py`                            | The actual Lambda function                                        |
| `bin/lambda/s3upload.py`                             | Triggered by API Gateway to upload a file to S3 (not implemented) |
| `bin/lambda/update_code.py`                          | Updates lambda function                                           |
| `cf/cf.yml`                                          | The complete CloudFormation template                              |
| `config/aws.ini`                                     | Config file for the CloudFormation python scripts                 |
| `data/data.sql`                                      | Sample data file 1                                                |
| `data/lorem.txt`                                     | Sample data file 2                                                |
| `supplied/DevOps-Engineer-EA-Applicant-Exercise.pdf` | The provided instruction file                                     |
| `supplied/data.sql`                                  | Sample data file 1                                                |

### Cost Details

| Product     | Cost details                                 | Per data sample      |
|-------------|----------------------------------------------|----------------------|
| S3          | $ 0.023 per GB for first 50 TB per Month     | $ 0.0000000000026186 |
| Lambda      | First 1M requests free, then $0.20 per 1M.   | $ 0.00               |
| SNS         | $2.00 per 100,000 emails.                    | $ 0.00001            |
| SQS         | Standard Queue: $0.40 per 1M requests.       | $ 0.00000040         |
| DynamoDB    | $1.25 per 1M writes, $0.25 per million reads | $ 0.0000015          |
| VPC         | None                                         | $ 0.0                |
| NAT Gateway | $ 0.045 per hour, $ 0.045 per GB             | $19.44/Month         |
| API Gateway | $3.50 for first 333M, $2.80 for next 667M    | $ (a teeny number)   |




