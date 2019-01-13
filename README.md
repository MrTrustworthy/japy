# JaPy

[![Build Status](https://travis-ci.com/MrTrustworthy/japy.svg?branch=master)](https://travis-ci.com/MrTrustworthy/japy)

## General
This is a small app allowing you to practice japanese characters. Currently, only Hiragana is supported. 

## TODO

* Add more character sets, and finally also words & small sentences. Will be done once I actually need them.
* Create user logins to save session progress on a user-basis
* Work on the UI. As it turns out, websites completely without CSS look shit.

## Deployment
If you want to deploy it yourself, fork it and create a travis CI pipeline with all the environment variables mentioned in `.travis.yml`. The DB is currently assumed to be PostgreSQL, and deployment works via helm onto a GKE K8s cluster with the docker images pushed to DockerHub. Either replicate that setup or adjust the CI config to your needs.