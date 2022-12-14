#
# <center>Welcome to this Cart Api&nbsp;[![Python package](https://github.com/LeandroLFE/Projeto-LuizaCode/actions/workflows/python-package.yml/badge.svg)](https://github.com/LeandroLFE/Projeto-LuizaCode/actions/workflows/python-package.yml)</center>

## This project is another implementation of the "Projeto-LuizaCode" from my friend [@anairotiv](https://github.com/anairotiv/Projeto-LuizaCode).  
## It consists of an API written in Python language that makes CRUD of a cart that contains User, Product, Cart and Cart-Items Schemas and uses FastAPI with MongoDB


# &nbsp;
# -> Libraries

## * To Production:
&nbsp;
### fastapi[all] = Fastapi Python framework with it´s aditional modules: requests and uvicorn used in this project
### motor = Driver Python Async for MongoDB
### python-dotenv = To read .env envinronment file for pytest

&nbsp;
## * To Format: 
### Black Formatter extension recommended
### isort to organize imports
### flake8 to lint
&nbsp;


## * To Test:
### pytest = Python library that extends unittest to do soffisticated testing.
### pytest-asyncio = library to work in Pytest asynchronous
### pytest-cov = library that add coverage report to pytest
### pytest-env = library to work with envinronment variables in pytest easily

# &nbsp;
# -> Installation Step by Step
&nbsp;
## Requirements: Git ;  Python >= 3.10 ; MongoDB Atlas string connection
&nbsp;
## In terminal:
### 1) Git clone this project 
```
$ git clone https://github.com/LeandroLFE/Projeto-LuizaCode.git
```
### 2) Move to the Project folder
```
$ cd Projeto-LuizaCode
```
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
### 6) Install dependences
```
$ pip install -r requirements.txt
```
### 7) Run
```
$ uvicorn main:app
```
### 8) Testing
```
Open http://127.0.0.1:8000/docs or use the http_tests folder with the VSCode extension "Rest Client" to send requisitions
```
# &nbsp;
# -> To use pytest:
## Run Tests
```
$ pytest
```
# &nbsp;
# -> Coverage Report:
## * You can add a folder to store the coverage reports, i.e. tests\coverage
## * You can edit .coveragerc file to configure what won´t be used in coverage
```
[run]
omit = tests/*, main.py
```
## Run Tests with coverage report
```
$ pytest --cov-config=.coveragerc --cov-report xml:{your_coverage_location}\cov.xml --cov-report term --cov=. tests/
```
* it will execute pytest, store the coverage report in cov.xml file, and show the result table in terminal
* You can use the VSCode "Coverage Gutters" extension to show coverage in each python file in project
