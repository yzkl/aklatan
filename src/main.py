from fastapi import FastAPI, Response


app = FastAPI()


@app.get("/")
def read_root() -> Response:
    return Response("The server is running.")