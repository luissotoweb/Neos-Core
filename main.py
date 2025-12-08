from fastapi import FastAPI

# Instancia de la aplicación.
app = FastAPI()

# Endpoint de prueba: GET en la ruta raíz (/)
@app.get("/")
def read_root():
    return {"message": "¡Nexus Core - Online! (V-0.0.1"}