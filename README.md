# Banners

### Introduction

This project includes a web application with a database and a spark job. 

The web application shows a simple form that requests a Campaign ID and then shows banners for that campaign that 
satisfies a certain business logic.

The spark job crunches the numbers provided in the CSV files and figures out what banners to show corresponding to a 
given campaign ID.

Everything has been included in a docker-compose file and does not require anything else (other than docker) to be 
installed on your local machine. No account needed on the cloud as well.

### Data

There are some CSV files that provide information about the campaigns and the banners and which banners resulted in a
conversion. The three kinds of CSV files are:

* impressions - `[banner_id, campaign_id]`
* clicks - `[click_id, banner_id, campaign_id]`
* conversions - `[conversion_id, click_id, revenue]`

The CSV files are located under `data`  directory. These files available for each quarter of an hour, for example, 
clicks_1.csv, clicks_2.csv, clicks_3.csv and clicks_4.csv and similarly for impressions and conversions.

Other than these, there are some banner images also included in the repo. These can be found under `banner_web_app/static`
directory.

### Prerequisites

Like already mentioned, all we need is a laptop with `docker` and `docker-compose` installed. And also `git`, to clone 
the repo.

### Behind the scenes

Before we learn how to tun the app, let's get a brief insight into what's happening behind the scenes when you run it.

The first step is to build the app and then run it. Building is a one time process which takes slightly longer but you 
should be good to simply run it after the first time.

There are two main components in this project:
* `banner_data_initializer` - this is a spark job that parses the CSV files provided, runs the business logic and computes
the final data for the client and stores it in MySql.
* `banner_web_app` - This is a `python-flask` web application that shows a simple form to the client and asks to enter a 
`Campaign ID` for which he/she wants to view the banners. The app integrates with the MySql to fetch the response and 
then renders an HTML page with the banners if they exist.

As you can see both these components connect to MySql, so it is important that MySql is up and running before they try 
to connect with it. I have added sufficient sleep time in both those components to fulfill that requirement. You can 
change that if you want and that would require you to build again for your change to take effect.

I have included a `stress_test.py` script to compute the time taken to run 5000 requests. This script needs to be 
run manually. See steps below for that.

I have also added `Redis` as a cache store for the web_app to serve the banners quickly. It's a cache store to the MySql 
backend database. During my tests, I finished 5000 requests in 18-19 seconds without `Redis` and ran the same set of 
requests in 6-7 seconds with `Redis`. That is a huge improvement of more than 65% in response time.

### Steps to run the app

* Clone the repo - `git clone <repo_clone_address>`
* Change to the repo directory - `cd banners`
* If you are running this for the first time, you need to build all the docker images. This is a one-time process unless 
you make changes to the project's Dockerfile(s). You need to run `docker-compose up --build`
* The next time you run the app, you do not need to build the docker images. You can simply run `docker-compose up` from 
the next time. In fact, the next time you do not need to spark job to run because you already processed the CSV files 
and stored the output in MySql for the web_app, so you could skip it by running 
`docker-compose up --scale banner_data_initializer=0`. 

You are able to do this because I have added the proper changes 
so that the MySql database persists after the first computation. Even if you delete the images and rebuild the containers. 
This is done through docker volumes.

### Steps to run the stress test

* Start the web app - `docker-compose up`. Ensure that the banner_web_app is running before proceeding.
* Open a separate terminal and run `docker ps`
* In the output, copy the `CONTAINER ID` for the `banner_web_app`
```buildoutcfg
CONTAINER ID   IMAGE                    COMMAND                  CREATED         STATUS         PORTS                                                  NAMES
7f50c803502e   banners_banner_web_app   "/bin/sh -c 'sleep 6…"   2 minutes ago   Up 2 minutes   0.0.0.0:8000->8000/tcp, :::8000->8000/tcp              banner_web_app
```
* Login to the RUNNING web app container - `docker exec -it <container_id> sh`
* You should be logged in to the `/app` directory. In any case, run the `stress_test.py` script using `python stress_test.py`.
* Wait for the results.