Load testing of COPS
====================

Load tests for COPS.

**Warning:** Be very careful before testing any production URLs! Speak with your team before doing so.

## Installation

<!-- TODO: Docker or Vagrant install -->

Installation for development purposes:

* Use Python3.
* Create and activate a virtualenv.
* Install requirements with `pip install -r requirements.txt`.

## How to run load tests

To run e.g. the backend jobs load test on localhost use:
```
locust -f backendjobs.py --host http://localhost:5001
```

and open the locust UI in your browser:   
[http://localhost:8089](http://localhost:8089)

To start a very simple load test set  
**users** to `100`  
and  
**hatch** rate to `10`

Start running the load test and see the result in your browser! :)

## Known issues

* Missing optimized Docker or Vagrant VM

This load tests on your local machine are very simple for development purposes. To run a more demanding "smoke" test 🔥 this load tests need to be run inside an optimized Vagrant VM or Docker with optimized internal network settings and DNS caching (to not load test the DNS query).