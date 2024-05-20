DyanoDB table operations fall into two categories:
- Control plane operations
    Used for managing tables, indexes, streams, capacity... e.g. create table, update table
    ![alt text](image-14.png)
    
- Data Plan operations
    Manipulate Items using CRUD actions e.g. create item, update item


Both types of operations can be called using AWS SDK/CLI...

DynamoDB uses JSON and REST over HTTP

The AWS CLI and management console use the DynamoDB SDK behind the scenes
![alt text](image-9.png)

SDK is available in many programming languages

The SDK exposes 3 types of interfaces:
- Low level interface
![alt text](image-10.png)
User of this interface must specify the data type (e.g. `{"name": {"S": "Tomer"}}`)

Example of low level interface using boto3 library in python:
![alt text](image-13.png)
As you can see we need the data descriptor

- Document Interface
![alt text](image-11.png)
Does not require developer to specify data types

- High level interface
![alt text](image-12.png)