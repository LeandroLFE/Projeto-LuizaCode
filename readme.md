#
# <center>Welcome to this Cart Api</center>

## This project is another implementation of the "Projeto-LuizaCode" from my friend [@anairotiv](https://github.com/anairotiv/Projeto-LuizaCode).  
## It consists of an API written in Python language that makes CRUD of a cart that contains User, Product, Cart and Cart-Items Schemas and uses FastAPI with MongoDB


# &nbsp;
# -> Libraries

## * To Production:
&nbsp;
### fastapi[all] = Fastapi Python framework with it´s aditional modules: requests and uvicorn used in this project
### motor = Driver Python Async for MongoDB

&nbsp;
## * To Format: Black Formatter extension recommended
&nbsp;


## * To Test:
### pytest = Python library that extends unittest to do soffisticated testing.
### pytest-asyncio = library to work in Pytest asynchronous
### pytest-cov = library that add coverage report to pytest
### pytest-env = library to work pass envinronment variables to pytest easily

# &nbsp;
# -> Installation Step by Step
&nbsp;
## Requirements: Git ;  Python >= 3.10 ; MongoDB Atlas string connection
&nbsp;
## In terminal:
### 1) Git clone this project 
```
git clone https://github.com/LeandroLFE/Projeto-LuizaCode.git
```
### 2) cd Projeto-LuizaCode
### 3) Add .env file at the root folder with this content:
```
DATABASE_URI = <your_mongodb_atlas_connection_string>
```
### 4) Create a Python virtual envinronment
```
$ python -m venv venv
```
### 5) Activate the envinronment
```
$ .\venv\Scripts\activate (Windows)
$ source venv/bin/activate (Linux)
```
### 6) Run
```
$ uvicorn main:app
```
### 7) Testing
```
Open http://127.0.0.1:8000/docs or use the http_tests folder with the VSCode extension "Rest Client" to send requisitions
```
# &nbsp;
# -> To use pytest:
## Add pytest.ini file with almost the same .env content:
```
[pytest]
env =
    DATABASE_URI = <your_mongodb_atlas_connection_string>
```
## Run Tests
```
$ pytest -c pytest.ini
```
# &nbsp;
# -> Coverage Report:
## * Add a folder to store the coverage reports, i.e. tests\coverage
## * You can edit .coveragerc file to configure what won´t be used in coverage
```
[run]
omit = tests/*, main.py
```
## Run Tests with coverage report
```
$ pytest -c pytest.ini --cov-config=.coveragerc --cov-report xml:tests\coverage\cov.xml --cov-report term --cov=. tests/
```
* it will execute pytest, store the coverage report in cov.xml file, and show the result table in terminal
* You can use the VSCode "Coverage Gutters" extension to show coverage in each python file in project
