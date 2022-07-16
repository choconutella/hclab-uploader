import logging
import os

def setup_logger(name:str, file:str):

  formatter = logging.Formatter("%(asctime)s - %(levelname)s : [%(pathname)s - %(lineno)d] %(message)s")
  handler = logging.FileHandler(os.path.join(os.getcwd(),f"logs\\{file}.log"))        
  handler.setFormatter(formatter)

  logger = logging.getLogger(name)
  logger.setLevel(logging.INFO)
  logger.addHandler(handler)

  return logger
