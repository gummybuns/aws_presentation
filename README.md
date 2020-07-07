# Hosting Projects for Cheap (Using Aws)

## Why

* Building things is fun
* Paying a lot of money for your projects is not

Leveraging AWS' microservices provides a very cheap way to host

### Example

* realzacbrown.com is hosted on an EC2 server
  * DNS configuration in NameCheap
  * mysql database (cms)
  * node + express api
  * static files hosted on server:
    * react frontend
    * index.html
    * main.css
  * nginx webserver
Costs ~$20/month

* wumbo.co uses AWS microservices
  * DNS configuration in Route53 (mostly)
  * DynamoDB database
  * Api Gateway + CloudFormation backend (Python Flask Application)
  * static files hosted on S3:
    * react frontend
    * index.html
  * S3 / CloudFront as the "webserver"
  * Lambda + SES to asynchronously send emails
Costs $0.55/month

### Cost Breakdown

* EC2 - you pay for server uptime.

* Route53 - $0.50/domain
* DynamoDB - $0.25/1M read request units + $1.25/1M write request units (I pay $0.04)
* Api Gateway - $3.50/1M requests (I pay $0)
* S3 - $0.02/GB
* CloufFront - $0.009/10K Requests
* SES - complicated, but I pay $0.01/month
* Lambda - 1M Free Requests per month + 400K Seconds Free (you pay for compute time)

### Pros / Cons of Microservice

#### Cons

* Learning Curve
* Non-traditional frustrating complexity
  * I know how to build a server and host a website so so easily on a normal server
    Why is it so much harder to do the same thing in AWS??
* Every blog/tutorial uses screenshots of the AWS web client
  * All servers are copy/paste of shell commands / config files
  * Using the aws web app is a much more manual process and therefore difficult reproduce
* Building latency into your application
  * Communicating with these services is done through api requests (more of a backend issue)

#### Pros

* $$$

## This Presentation Includes

* Just the frontend piece (for time + complexity)
* Configuration instead of screenshots
  * Use boto3 + aws-cli instead of the webapp for reproducible setup

## Setting up AWS

* Sign up for aws at https://aws.amazon.com/free/
  * It will ask for personal info + credit card!

### What is IAM
* In terms of a traditional server, think of IAM as a way to manage a servers users and groups
  * In order to remotely access AWS Services you need to create a user with the proper permissions to access those services
  * Similar to a server, you dont want to create a user that has sudo privileges to everything

## Setup the aws cli
* Download and then run `aws configure`

## Setup boto3
* I prefer to use boto3 to the aws cli so i can write scripts 

### S3 - File hosting
#### Manually
* Go to s3 -> create bucket -> add name -> make sure public save
* Go to properties -> Static Website Hosting -> use for hosting -> specify index.html
* Go to permissions -> Bucket Policy -> Paste:
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "s3:GetObject"
            ],
            "Resource": [
                "arn:aws:s3:::MY_BUCKETNAME/*"
            ]
        }
    ]
}
```

* Upload index.html (hello world) -> Manage permissions: Public Read Access

#### Scripted
`scripts/http_bucket.py`
* Show that it worked the exact same
* `aws s3 sync ./frontend/hello_world/ s3://testcli4.zacgroove.com`

#### React
We can use the sync as part of our package.json

* Run the script and deploy to s3
* It is breaking: Why - because the url react is using is incorrect

We can go through hoops to set up react to use the proper urls for the static files, but since we are going to eventually have our own website with a proper root url, its not worth doing at this time

### Route 53 - DNS
Go to route53 - create a fake hosted zone

* It will create a bunch of NS records. These need to be set in your DNS provider for the domain you purchased as the nameservers

You can also script this to create the zone and print those records for you:

#### Manual - update your DNS
Go in and update your nameservers

### Hook Route53 --> S3
Your bucket name must be the same as your domain/sub-domain
Good thing for our scripts!!

Manually create the record. Show it works!
Use the script to create the record for a different domain. Show that it works

### CloudFront
Its kind of a bummer that it is not https. We can use cloudfront to setup secure connections and we get the extra benefit of speed improvements through caching

**IMPORTANT** Creating a Cloudfront Distribution caches the shit out of your application. We dont want to cache our index.html page ever because we want to ensure that we deliver our changes immediately. In order to prevent this file from caching, we can add the Cache-Control header to this specific file in s3. The new frontend deploy script becomes:

```
npm run build && \
  aws s3 cp --cache-control 'max-age=0' ./build/index.html s3://my.bucket.com && \
  aws s3 sync --exclude index.html ./build s3://my.bucket.com
```

This is the single most frustrating thing of using aws because Cloudfront takes forever to reload. Lets not make this mistake now and save some hair.

#### Create the ssl certificate
* Go to ACM -> create certificate -> add route53 records -> wait
* Use `scripts/create_ssl.py`

#### Create the Distribution
* Origin Domain Name should be the name of the s3 bucket used for website hosting (can be found in s3 -> properties website hosting: endpoint)
* Origin Id should be a unique string
* We want to redirect to https
* Choose the ssl certificate we created in ACM
* *Important* CNAMEs must include the bucket name. Otherwise it cant be used in route53 properly
* Save

Since Cloudfront is a CDN with heavy caching, in order to ensure everyone has the latest everything all the time, we can just prevent any sort of caching of the html files. We wont get the same speed performances but since this is for small projects, its more important to make sure we can deliver changes quickly. (If you wanted to you could instead make a request to invalidate the cache everytime you upload to s3, but this costs like $0.50 every time)

Click on the distribution -> Behaviors -> Create Behavior

* Path Pattern is `*.html`
* Set the TTL Values to all Zero Save

Now we need to update our route53 config to instead have the alias point to our cloudfront distribution.

**Note** If you dont see the cloudfront distribution, its because you forgot to add it as a CNAME when configuring the distribution

All of this is also automated with the `scripts/create_cloudfront.py`

### Routing - Lamdda Edge
Using the hash router is kinda lame - for users its not easy to remember for crawlers i dont even think it works. We want to use the Browser router to make sure that people can visit our routes directly. But for local development we want to continue to use Hash Router so we dont need to setup any sort of webserver to access different pages

#### Update Frontend
We need to update our application to use the correct type of router conditionally

#### Cloudfront Routing Lambda@Edge
We can use a lambda@edge function to process all requests to cloudfront.

* If the request does not end in a file extension, it is likely a route that should be served by our application
* If the request does end in a file extension serve it as is


The benefits to this is it allows for us to use a browser router with our application. The downside is we will not be serving 404 errors for bad routes with this approach. All http requests will be a 200 and our react application will need to do something to handle bad routes.

This is not worth doing manually, lets just automate this process, similar to how we sync our s3 bucket.

##### Create Role
https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/lambda-edge-permissions.html

1. iAM -> Create Role -> Click Lambda
1. Permissions: AWSLambdaRole -> Save Everything
1. Edit The Trust relationships of the role. The Service should be an array `["lambda.aws.com", "edgelambda.amazonaws.com""]`

#### Create the lambda function
1. Create Lambda Function -> Author From Scratch
1. Enter a name
1. Choose Python runtime
1. Use Existing Role -> the one we just created
1. Copy/Paste the code from `frontend/lambda/routing/lambda_function.py`
1. Save
1. Actions -> Publish Version
1. Actions -> Deploy to Lambda@Edge
