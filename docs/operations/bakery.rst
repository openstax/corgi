.. _operations-updating-bakery-scripts:

===========================
Update COPS Bakery Scripts 
===========================

build-push-bakery script - 

uses build-bakery
(set the tag)
export tag 



build-bakery script - 
for development


-------

generate script and push to docker. 


development vs production


export a tag for development  nad build and look at it. 
if you need to test with concourse build push 


production 
build-push

=====
Local 
=====
- Make sure the enviconemntt  variables for the envirconment you  wan tto 

buidl pipeline for is correct  
```
bakery/env/<environment>.json 
```

Build Pipeline in bakery/ directory:
```
./build pipeline distribution local -o distribution-pipeline.local.yml
```

-- docker-compose up, concourse server on port :8100

- Set up local concourse target - Note this version is a more updated version

than what is in production
```
fly -t cops-dev login -c http://localhost:8100 -u dev -p dev
```

- See concourse server targets

```
fly targets
```

Will most likely prompt you to sync -
```
fly -t cops-dev sync
```

Set the pipeline to the concourse server target - 
```
fly -t cops-dev sp -p distribution-pipeline -c distribution-pipeline.local.yml
```

Unpause Pipeline:
```
fly -t cops-dev unpause-pipeline -p distribution-pipeline
```

- Let  it be known as to what the triggers the pipeline:

https://github.com/openstax/output-producer-service/blob/master/bakery/distribution-feed.json
- Let it be known how the s3 bucket needs to be set updated
--- Enable version if not Concourse S3 resource will give a versioning error.
--- Bucket region/ access
--- Distribution-feed.json file that (temporary) triggers pipeline
--- Can be seen on localhost:8100

==========
Production
==========
-  Make sure the enviconemntt  variables for the envirconment you  wan tto 

buidl pipeline for is correct  bakery/env/<environment>.json 

Build Pipeline in bakery/ directory:
./build pipeline distribution local -o distribution-pipeline.local.yml

- Assuming  you have your concourse target set up -
- We don't have a "staging" concourse server, you have to know what your pipeline is

Set Pipeline in concourse with config file:
fly -t cops-dev sp -p distribution-pipeline -c distribution-pipeline.local.yml

Unpause Pipeline:
fly -t cops-dev unpause-pipeline -p distribution-pipeline