# AWS Serverless File Processing System — Cloud/DevOps Project

This is my cloud project where I built an event-driven pipeline that automatically processes uploaded sales CSV files. I used **Terraform** to create all the infrastructure as code and **LocalStack** (running in Docker) to emulate AWS on my laptop, so the whole project ran locally with no AWS account and no charges. The goal was to learn how real cloud services connect together: storage, queues, serverless functions, databases, permissions and failure handling.

---

## What the System Does

When a CSV file is uploaded, the system automatically:

1. Stores it in **S3**
2. Sends a message to an **SQS** queue
3. Triggers a **Lambda** function (Python) that reads the file and calculates total products sold, total revenue and the highest-quantity product
4. Saves the result to **DynamoDB** with a `SUCCESS` or `FAILED` status
5. Moves messages that fail 3 times to a **dead-letter queue**

```
CSV upload -> S3 -> SQS -> Lambda -> DynamoDB
                     |
                     +-- after 3 failed attempts --> Dead-letter queue
```

Example input (`monthly_sales.csv`):

| Product | Quantity | Price |
|---------|----------|-------|
| Laptop | 5 | 1000 |
| Mobile | 10 | 500 |
| Keyboard | 20 | 50 |
| Mouse | 15 | 25 |

Result: **50 products sold, $11,375 revenue, top product Keyboard.**

---

## Folder Structure

```
aws-serverless-csv-pipeline/
│   docker-compose.yml        Starts LocalStack in Docker
│   .env                      LocalStack auth token (not uploaded to Git)
│   .gitignore                Keeps secrets and Terraform files out of Git
│   README.md                 This file

terraform/
│   provider.tf               Points the AWS provider at LocalStack
│   s3.tf                     S3 bucket
│   sqs.tf                    Main queue and dead-letter queue
│   notification.tf           S3 -> SQS permission and notification
│   dynamodb.tf               Results table
│   lambda.tf                 Lambda function, IAM role/policy, SQS trigger

lambda/
│   handler.py                Lambda entry point (SQS -> S3 -> DynamoDB)
│   processor.py              CSV calculation logic

sample-data/
│   monthly_sales.csv         Valid test file
```

---

## Tools and Services I Used

| Tool / Service | What I used it for |
|----------------|-------------------|
| `Docker` | Running LocalStack in a container |
| `LocalStack` | Emulating AWS locally at `localhost:4566` |
| `Terraform` | Creating all resources from code (Infrastructure as Code) |
| `AWS CLI` | Uploading files and checking results by hand |
| `Python` | Reading the CSV and calculating the results |
| `S3` | Storing the uploaded CSV files |
| `SQS` | Queuing one message per uploaded file |
| `Lambda` | Running the processing code automatically |
| `DynamoDB` | Storing one result per file |
| `IAM` | Giving Lambda only the permissions it needs |

---

## How to Run This Project

1. Clone this repository:
```powershell
git clone https://github.com/AnmolSrivastav/aws-serverless-csv-pipeline.git
cd aws-serverless-csv-pipeline
```
2. Install Docker Desktop, Terraform, the AWS CLI and Python 3.
3. Create a free account at https://app.localstack.cloud and copy your auth token.
4. Create a `.env` file in the project root:
```
LOCALSTACK_AUTH_TOKEN=your-token-here
```
5. Start LocalStack and wait about 30 seconds:
```powershell
docker compose up -d
```
6. Create the infrastructure:
```powershell
cd terraform
terraform init
terraform apply
```
Type `yes` when asked.

7. Set dummy credentials for the AWS CLI (this terminal session only):
```powershell
$env:AWS_ACCESS_KEY_ID="test"
$env:AWS_SECRET_ACCESS_KEY="test"
$env:AWS_DEFAULT_REGION="ap-southeast-2"
```
8. Upload a file and view the results (wait about 20 seconds on the first run):
```powershell
aws --endpoint-url=http://localhost:4566 s3 cp sample-data\monthly_sales.csv s3://sales-reports-bucket/
aws --endpoint-url=http://localhost:4566 dynamodb scan --table-name file-processing-results
```
9. Inspect failed messages:
```powershell
aws --endpoint-url=http://localhost:4566 sqs receive-message --queue-url http://localhost:4566/000000000000/file-processing-dlq
```

> LocalStack does not save data. After restarting the container, run `terraform apply` again to recreate the resources.

**To clean up:**
```powershell
cd terraform
terraform destroy
cd ..
docker compose down
```

---

## Key Findings

- **Queues make systems reliable.** SQS sits between S3 and Lambda, so no file is lost if Lambda is busy or fails.
- **A dead-letter queue stops endless retries.** Bad files are set aside for inspection instead of looping forever.
- **Infrastructure as Code is repeatable.** Because LocalStack forgets everything on restart, one `terraform apply` rebuilds the whole system in under a minute.
- **Least-privilege IAM matters.** Lambda only has the few permissions it needs.
- **Testing finds hidden bugs.** The empty-file case looked like a success until I tested it.
- **Re-uploading a file with the same name overwrites its result**, because `file_name` is the table key.
