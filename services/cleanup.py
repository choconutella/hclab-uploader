from datetime import datetime
import time
import os
import queue
from services.service import Service
from hclab2.log import setup_logger

today = datetime.today().strftime("%Y%m%d")
logger = setup_logger("cleanup", f"cleanup_{today}")


class CleanUp(Service):
  
  def __init__(self, config):
    super(CleanUp, self).__init__()
    self.today = datetime.today()
    self.config = config
    self.message = queue.LifoQueue()

  def run(self):
    
    time.sleep(1)

    logger.info("CleanUp thread is runnning...")

    while self._runner.is_set():
      
      try: 
        self.__process()
      
      except ValueError as error:
        logger.error(error)
        self.message.put(error)
        continue

      time.sleep(1) 
      

  def __process(self):

    counter = 1

    while "f"+str(counter) in self.config["cleanup"]:
      
      content = self.config["cleanup"][ "f"+str(counter)]
      
      path = content.split(",")[0]
      timer = content.split(",")[1]

      for filename in os.listdir(path):

        file = os.path.join(path,filename)

        if not os.path.isdir(file):

          file_date = datetime.fromtimestamp(os.path.getmtime(file))
          
          duration = self.today - file_date
          if duration.days > int(timer):
            logger.info(f"Deleting {file}")
            self.message.put(f"Deleting {os.path.basename(file)}")
            os.remove(file)

      counter += 1