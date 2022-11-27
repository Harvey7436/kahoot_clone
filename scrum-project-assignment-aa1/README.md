[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-c66648af7eb3fe8bc4f294546bfd86ef473780cde1dea487d3c4ff354943c9ae.svg)](https://classroom.github.com/online_ide?assignment_repo_id=8146188&assignment_repo_type=AssignmentRepo)


## setup virtual environment

```
$ python -m venv .venv
```

Activate virtual environment

```
$ source .venv/bin/activate
```

(Optional if needed) In case of windows not allowing to run scripts on the terminal
```
$ Set-ExecutionPolicy Unrestricted -Scope Process
```

## load packages

```
pip install --upgrade pip
pip install -r requirements.txt

```

in case you install additional packages.... update the requirements.txt with:

```
pip freeze > requirements.txt

```

# Database migration steps
DO THIS AFTER EVERY CHANGES MADE TO "models.py"
```
$ flask db migrate
$ flask db upgrade
```


# Running flask

```
$ flask run
```
