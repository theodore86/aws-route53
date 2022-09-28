# AWS Route53 SDK

## Features:
- AWS route53 resource record sets cleanup mechanism

## Usage:

#### Copy the AWS credentials
You can get the credentials from:  
``AWS management console -> Command line or programmatic access``

#### Export the AWS credentials
```bash
export AWS_ACCESS_KEY_ID="..." \
       AWS_SECRET_ACCESS_KEY="..." \
       AWS_SESSION_TOKEN="..."
```

#### Dry-run before any AWS Route53 resource record deletion:
```bash
python3 record_cleanup.py --dryrun --regex '.*record.*' --aws-hosted-zone myzone.test.co
```

#### Delete the AWS Route53 resource records in the selected zone:
```bash
python3 record_cleanup.py --regex '.*record.*' --aws-hosted-zone myzone.test.co
```

#### Delete the AWS Route53 resource records using docker:
```bash
docker build -t aws_route53:latest .
docker run --rm -it aws_route53:latest \
  -e AWS_ACCESS_KEY_ID="..." -e AWS_SECRET_ACCESS_KEY="..." -e AWS_SESSION_TOKEN="..." \
  --regex '.*pattern.*' --aws-hosted-zone <name>
```
