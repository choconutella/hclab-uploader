import time 
from datetime import datetime
import os
from shutil import copy
import queue
import requests
import sqlalchemy as db

from hclab2.patient import Patient
from hclab2.log import setup_logger
from services.service import Service

today = datetime.today().strftime("%Y%m%d")
logger = setup_logger("api", f"api_{today}")


class Email (Service):

  def __init__(self, config, hclabConnection):
    super(Email, self).__init__()
    self.message = queue.LifoQueue()
    self.config = config
    ora = config['hclab']
    self.hclabConnection = db.create_engine(f"oracle://{ora['user']}:{ora['pass']}@{ora['host']}:{ora['port']}/{ora['db']}")


  def run(self):

    time.sleep(1)    

    while self._runner.is_set():

      for filename in os.listdir(self.config['pdf']['source']):
        file = os.path.join(self.config['pdf']['source'],filename)
        if os.path.isdir(file):
          pass
        else:
          if file.endswith('.pdf'):
            self.message.put(f"Processing {filename}")
            try:
              self.__process(file)

            except ValueError as error:
              logger.error(error)
              self.message.put(error)
              copy(file,os.path.join(self.config['pdf']['err'],os.path.basename(file)))
              os.remove(file)
              
            except Exception as exc:
              logger.info(exc)
              self.message.put(exc)

            finally:

              continue

          else:
            os.remove(file)

      time.sleep(5) 


  def __process(self,file:str):
    '''
    File PDF will be processed to API 

    Parameter: 
      file : str 
          Path of result file
    '''
    filename = os.path.basename(file)

    # adjust lno based filename here
    lno = os.path.splitext(filename)[0].split('_')[3]

    # get patient data
    try:
      patient = Patient(self.hclabConnection, lno)
    except ValueError as e:
      raise ValueError(e)

    files = {"file" :  open(file, "rb")} 
    values = {"pid" : patient.pid}

    logger.info(f"Upload file : {file}")
    logger.info(f"Payload : {values}")
    response = requests.post(self.config["api"]["base_url"], files=files, data=values)

    logger.info(f"{response.status_code} - Response : {response.json()}")
    if response.status_code not in [200,201]:
      raise Exception(f"Failed to sent. Status code : {response.status_code}. Response : {response.json()}")
      
    # backup pdf that already processed to temp_pdf folder
    copy(file, os.path.join(self.config['pdf']['backup'],filename))
    os.remove(file)

