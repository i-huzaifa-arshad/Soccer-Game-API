# Soccer Online Game Manager App API

A Django REST Framework based project for Soccer API app. The API includes features such as user registration, login, player transfer, player buy and more.

## Getting Started

Following instructions will help you on how to setup and use this project on your local machine.

## Prerequisites

- Python installed on your system

## Installation

1. Clone the repository:
```
git clone https://github.com/i-huzaifa-arshad/Soccer-Game-API
```

2. Navigate to the project directory:

```
cd Soccer-Game-API
```

3. Create a virtual environment:
- For Ubuntu/Linux:
  ```
  python3 -m venv env
  source env/bin/activate
  ```
- For Windows 10/11:
  ```
  py -m venv env
  .\env\Scripts\activate
  ```
4. Install the required packages:
```
pip install -r requirements.txt
```
5. Apply the migrations:

```
python manage.py migrate
```

6. Create a superuser in order to use admin panel:

```
python manage.py createsuperuser
```
7. Run the server:

```
python manage.py runserver
```

## Swagger API Documentation

Open `http://localhost:8000/` or `http://127.0.0.1:8000/` when the server is running to see the Swagger API documentation.

- The `signup` and `login` endpoints do not need authentication from user.
- For other endpoints, a `Token` is required to use the endpoints.
- When user login, a token is generated. Use that token to access other endpoints:
    - Click on `Authorize` button on homepage of Swagger documentation.
    - Under value, write `Token #token` and click `Authorize`, where the `#token` can be something like `8544caa04d945327fc44417d17038700f2daa90c`.
    - Now, you can use all other endpoints without any trouble.
