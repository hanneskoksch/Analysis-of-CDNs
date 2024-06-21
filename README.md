# Python virtual environemnt

https://python.land/virtual-environments/virtualenv

Create:

```bash
python3 -m venv venv
```

Use:

```bash
source venv/bin/activate
```

Deactivate:

```bash
deactivate
```

Delete:

```bash
rm -r venv
```

# Requirements

https://python.land/virtual-environments/installing-packages-with-pip

Install requirements:

```bash
pip install -r requirements.txt
```

Set requirements:

```bash
pip freeze > requirements.txt
```

# Others

```bash
python -m venv venv
source venv/bin/activate
pip install jupyter
ipython kernel install --user --name=venv
jupyter notebook
```
