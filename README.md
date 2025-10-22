## USAGE
How to run?

first install requirements ```py -m pip install -r requirements.txt```
Then you should input MONGO_URI (get it from mongodb), EMAIL_ID, EMAIL_PASSWORD to send verification emails (currently works with gmail)
the run the app with ```py app``` (testing only)
or using gunicorn (for hosting in server or to run in linux based distributions)
```gunicorn app```

