"""
Opens a Jesse Crossen GUI (TT board) on a local server.
Board can then be set up in GUI and downloaded as image via specific button.
This image is then used translator_image_to_code.py

"""

# start script with the following arguments in command line
# ray start --head
# serve start --http-host=127.0.0.1

# standard library imports
import os

# 3rd party imports
import ray
from ray import serve
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# local imports (i.e. our own code)
from aux_image_to_code import Translator
# noinspection PyUnresolvedReferences
from utilities import utilities

# initialise FastAPI API instance
app = FastAPI()


@serve.deployment
@serve.ingress(app)
class TranslationLayer:
    translator: Translator

    def __int__(self):
        app.add_middleware(
            CORSMiddleware,
            allow_origins=['*', "http://localhost", "http://localhost:8080"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        pass

    @app.get("/t2/{matrix}")
    def translation2(self, matrix: str):
        """
        Route that accepts a matrix encoded as a string and calls the appropriate Translator function to convert it
        to bugbit code.

        :param matrix: matrix coded as string
        :return: None
        """
        self.translator = Translator()
        self.translator.matrix_to_bugbit_code(matrix)
        return None

    @app.post("/t2")
    async def get_body(self, request: Request):
        """
        Alternative route to translate a matrix coded as string to bugbit code.

        :param request: request object
        :return: None
        """

        self.translator = Translator()
        var = await request.json()
        self.translator.matrix_to_bugbit_code(var)


if __name__ == "__main__":
    # start ray server
    os.system("ray stop")
    os.system("ray start --head")
    os.system("serve start --http-host=127.0.0.1 --http-port=8000")

    ray.init(address="auto", ignore_reinit_error=True, namespace="serve")
    serve.start(detached=True)  # or False

    TranslationLayer.deploy()
    # start TTSIM GUI
    os.chdir(os.environ['TTSIM_PATH'])
    os.system("make server")
    os.chdir(os.getcwd())
