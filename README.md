[![Linting](https://github.com/theodore86/aws-route53/actions/workflows/build-and-publish.yml/badge.svg)](https://github.com/theodore86/aws-route53/actions/workflows/build-and-publish.yml)

# AWS Route53 SDK
Delete/Cleanup [resource records sets](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/rrsets-working-with.html) from the selected hosted zone of the AWS Route53.

## Features:
- AWS route53 resource record sets cleanup mechanism:
  - Supports `dry-run` mode before any resource record deletion.
  - Supports `regex` to include resource records for deletion.

## Usage:

#### Copy the AWS credentials
You can get the credentials from:  
``AWS management console -> Command line or programmatic access``

#### Export the AWS credentials
```bash
export AWS_ACCESS_KEY_ID=<value> AWS_SECRET_ACCESS_KEY=<value> AWS_SESSION_TOKEN=<value> (`optional-MFA`)
```

#### Install the required dependencies
```bash
pip3 install --user requirements.txt
```

#### Dry-run before any AWS Route53 resource record deletion:
```bash
python3 record_cleanup.py --dryrun --regex '.*record.*' --aws-hosted-zone myzone.test.co
```

#### Delete the AWS Route53 resource records in the selected zone:
```bash
python3 record_cleanup.py --regex '.*record.*' --aws-hosted-zone myzone.test.co
```

#### Delete the AWS Route53 resource records using ``Docker`` (recommended):
```bash
docker build -t aws_route53_cleaup:latest .
docker run --rm -it aws_route53_cleanup:latest \
  -e AWS_ACCESS_KEY_ID=<value> -e AWS_SECRET_ACCESS_KEY=<value> -e AWS_SESSION_TOKEN=<value> \
  --regex '.*pattern.*' --aws-hosted-zone <name>
```
