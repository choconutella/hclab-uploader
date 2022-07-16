import time 
from datetime import datetime
import os
from shutil import copy
import queue

import sqlalchemy as db

from hclab2.patient import Patient
from hclab2.mail.mailer import Mailer
from hclab2.mail.validate import Validate as MailValidator
from hclab2.log import setup_logger
from services.service import Service

from query.email_log import save_log

today = datetime.today().strftime("%Y%m%d")
logger = setup_logger("mail", f"mail_{today}")


class Email (Service):

  def __init__(self, config):
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
              continue

            except Exception as exc:
              logger.error(exc)
              self.message.put(exc)
              continue

          else:
            os.remove(file)

      time.sleep(5) 


  def __process(self,file:str):
    '''
    File PDF will be emailed 

    Parameter: 
      file : str 
          Path of result file
    '''
    filename = os.path.basename(file)

    # adjust lno based filename here
    lno = os.path.splitext(filename)[0].split('_')[3]

    # get patient data
    try:
      patient = Patient(self.hclabConnection,lno)
    except ValueError as e:
      raise ValueError(e)


    self.message.put(f"Processing {lno}")
    email = patient.email
    attachment_password = patient.birth_dt


    logger.info(f"Processing {file}")
                        

    # check avaibility email address
    if email == '' and email is None and email.lower() == 'noemail@none.com':
      save_log(self.hclabConnection, lno, email, 'FAIL', 'Email recipient empty')
      raise ValueError(f'Lab No. {lno} has not have valid phone number')


    validate = MailValidator(self.hclabConnection, lno)
    
    # only (nth) sent email
    # exit if current lab no already success sent email
    if not validate.has_repeated(2):
      raise ValueError(f'Lab No. {lno} has already sent message')

    # validating email requirement
    valid, message = validate.all()
    if not valid:
      save_log(self.hclabConnection, lno, email, 'NOT SENT', message)
      raise ValueError(f'Lab No. {lno} has exclude condition => {message}')

    mailer = Mailer(
      self.config["email"]["address"], 
      self.config["email"]["password"],
      self.config["email"]["name"],
      self.config["email"]["host"],
      self.config["email"]["port"]
    )
    subject = f"Hasil Laboratorium {patient.name}"
    attachment = mailer.encrypt_attachment(file, lno, attachment_password)
    try:
      mailer.send(email, subject, attachment)
    except Exception as e:
      raise Exception(f"Lab No. {lno} cannot sent email. {e}")
    
    save_log(self.hclabConnection, lno, email, 'SENT', message)
      
    # backup pdf that already processed to temp_pdf folder
    copy(file, os.path.join(self.config['pdf']['backup'],filename))
    os.remove(file)

