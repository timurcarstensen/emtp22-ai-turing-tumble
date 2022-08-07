"""
utilities
=========
This file contains various utility functions. The primary purpose is to set the environment variable
JAR_PATH to the path to the jar file that contains the java classes needed for the various environments in this project.
"""

# standard library imports
import os
import pathlib
import warnings

# 3rd party imports
# noinspection PyPackageRequirements
import jpype

# setting environment variables for the path to the JAR file and the data directory
artifact_directory: str = ""
artifact_file_name: str = ""

# throw ValueError if the user did not fill in artifact_directory or artifact_file_name during setup process
if not artifact_directory or not artifact_file_name:
    raise ValueError("artifact_directory and artifact_file_name must be set")

relative_jar_path = f"/../../out/artifacts/{artifact_directory}/{artifact_file_name}"

# path to jar file
os.environ["JAR_PATH"] = f"{pathlib.Path(__file__).parent.resolve()}" \
                         f"{relative_jar_path}"

# path to openai-gym-environments module
os.environ["REINFORCEMENT_LEARNING_DIR"] = f"{pathlib.Path(__file__).parent.resolve()}/../../reinforcement_learning"

# path to Turing Tumble simulator
os.environ["TTSIM_PATH"] = f"{pathlib.Path(__file__).parent.resolve()}/../../ttsim"

# check if wandb_key_file exists
if not os.path.exists(f"{os.getenv('REINFORCEMENT_LEARNING_DIR')}/wandb_key_file"):
    raise FileNotFoundError(f"wandb_key_file not found in.\n"
                            f"Please create a file called wandb_key_file in {os.getenv('REINFORCEMENT_LEARNING_DIR')} "
                            f"and put your wandb api key in it (cf. https://docs.wandb.ai/quickstart).")

# check if the wandb_key_file is empty
if os.stat(f"{os.getenv('REINFORCEMENT_LEARNING_DIR')}/wandb_key_file").st_size == 0:
    raise ValueError("wandb_key_file is empty; please set the wandb key in the wandb_key_file"
                     " (cf. https://docs.wandb.ai/quickstart).")

# export wandb key to WANDB_API_KEY environment variable
os.environ["WANDB_API_KEY"] = open(f"{os.getenv('REINFORCEMENT_LEARNING_DIR')}/wandb_key_file", "r").read()

# start JVM

# noinspection PyUnresolvedReferences
if not jpype.isJVMStarted():
    # noinspection PyUnresolvedReferences
    jpype.startJVM(classpath=os.getenv("JAR_PATH"))

# filter UserWarnings, FutureWarnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
