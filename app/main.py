from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def root():
    return {'message': 'Fuel Alert API V1.1 läuft!'}
