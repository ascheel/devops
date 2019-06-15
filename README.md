# devops

## Adobe DevOps Exercise

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
