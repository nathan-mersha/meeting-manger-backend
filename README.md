# Folder Structure

### Cred

This is where arranges environment variables will be stored based on the needed scenarios. This values include database name, url, token encrytper secret, twillio account datas, file upload path. This values will depend on scenarios like running tests or in production


### DAL

This directory is where the data access layer scripts are, this specific services connects to MongoDB, but if this script is modified, the server will be able to access other types of databases

### LIB

This directory is where client communction via email/sms scripts is located. The shared script is where some user related functionalities is located

### MODEL

This directory is where data base schema is located

### ROUTERS

This directory is where routing files are located

### JENKINS FILE

This file contains the pipeline script


### JENKINS FILE NGINX SERVER

This file contains the pipline script for the nginx server

### MAIN

Starting file for the FastAPI server

### NGINX CONF

Reverse proxy nginx config file

### REQUIREMENTS

This file contains dependencies for the server
