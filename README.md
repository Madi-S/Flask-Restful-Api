# Flask-Restful-Api
Tutorial for building RESTFul API with Flask

## Run Redis Queue:

```bash
rq worker --with-scheduler
```

## Run Web App:


####  Option 1 (simple)
```bash
python run.py
```


#### Option 2 (uWSGI)

```bash
uwsgi app.ini
```
