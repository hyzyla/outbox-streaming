# Example of FastAPI + SQLAlchemy


# Install
```shell
# create new virtual environment
python3 -m venv venv

# activate virtual environment
source venv/bin/activate

# install project dependencies
pip install -r requirements.txt
```


# Add new dependency
```shell
# Regenerate requirements.txt and install dependencies to virtual environment
pip-compile && pip-sync
```


# Run

run watchfiles in separate terminal tab
```shell
watchfiles "pip install ../.." ../../outbox_streaming
```

```shell
# Run database
docker-compose up && 

# Run web server
uvicorn app.main__session:app --reload
```
