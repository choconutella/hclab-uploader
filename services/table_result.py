import time 
from datetime import datetime
import os
from shutil import copy
import queue
import sqlalchemy as db

from hclab2.log import setup_logger
from hclab2.hl7.r01 import R01
from hclab2.item import Item
from hclab2.bridge.result import Result
from services.service import Service
from query.delete_detail import delete
from query.post_detail import save_detail
from query.post_header import save_header

today = datetime.today().strftime("%Y%m%d")
logger = setup_logger("result", f"result_{today}")

class TableResult (Service):

  def __init__(self, config):
    super(TableResult, self).__init__()
    self.message = queue.LifoQueue()

    self.config = config
    ora = config['hclab']
    self.hclabConnection = db.create_engine(f"oracle://{ora['user']}:{ora['pass']}@{ora['host']}:{ora['port']}/{ora['db']}")

    his = config['his']
    self.hisConnection = db.create_engine(f"mssql+pyodbc://{his['user']}:{his['pass']}@{his['dsn']}")

  def run(self):

    time.sleep(1)    

    logger.info("Result thread is runnning...")

    while self._runner.is_set():
      
      print("From Result")

      # for filename in os.listdir(self.config['file']['hl7_out']):
      #   file = os.path.join(self.config['file']['hl7_out'],filename)
      #   if os.path.isdir(file):
      #     pass
      #   else:
      #     if file.endswith('.R01'):
      #       self.message.put(f"Processing {filename}")
      #       try:
      #         self.__process(file)

      #       except ValueError as error:
      #         logger.error(error)
      #         self.message.put(error)

      #         copy(file,os.path.join(self.config['file']['err_result'],os.path.basename(file)))
      #         os.remove(file)
      #         continue

      #     else:
      #       os.remove(file)

      time.sleep(5) 


  def __process(self,file:str):
    '''
    File result will be inserted to HIS Result table

    Parameter: 
      file : str 
          Path of result file
    '''
    r01 = R01(file)
    counter = 1
    profile = False
    status = ''

    while 'obx'+str(counter) in r01.obx:

      obx = r01.parse_obx(r01.obx['obx'+str(counter)])

      # delete when status is 'D'
      if obx['status'] == 'D' : 
        delete(self.hisConnection,r01.ono,obx['test_cd'])
        counter += 1
        continue

      if obx['test_cd'] == 'MBFTR':
        obx.update(test_cd = r01.order_testid, test_nm = r01.order_testnm)

      result_value = obx['result_value'] if obx['data_type'] != 'FT' else ''
      result_ft = obx['result_value'] if obx['data_type'] == 'FT' else ''

      item = Item(self.hclabConnection, obx['test_cd'],lno=r01.lno)

      disp_seq = f'{item.group_seq}_{item.seq}_{("000"+str(counter))[-3:]}' 

      # save detail
      result = Result(
        self.hclabConnection,
        r01.lno,
        r01.ono,
        ("000"+str(counter))[-3:],
        obx['test_cd'],
        obx['test_nm'],
        obx['data_type'],
        result_value,
        result_ft,
        obx['ref_range'],
        obx['unit'],
        obx['flag'],
        obx['status'],
        obx['test_comment'],
        disp_seq,
        r01.order_testid,
        r01.order_testnm,
        item.group_name,
        item.parent,
        self.config['his']['site']
      )

      save_detail(self.hisConnection, result)

      # check is it profile test
      if result.order_testid != obx['test_cd']:
        profile = True
        status = obx['status']
      
      counter += 1

    if profile:

      item = Item(self.hclabConnection, r01.order_testid,lno=r01.lno)
      disp_seq = f'{item.group_seq}_{item.seq}_000' 

      # save test header
      result = Result(
        self.hclabConnection,
        r01.lno,
        r01.ono,
        '000',
        r01.order_testid,
        r01.order_testnm,
        'ST',
        '',
        '',
        '',
        '',
        '',
        status,
        '',
        disp_seq,
        r01.order_testid,
        r01.order_testnm,
        item.group_name,
        '000000',
        self.config['his']['site']
      )
      save_detail(self.hisConnection, result)


    # save header
    save_header(self.hisConnection, r01, self.config['his']['site'])


    if os.path.exists(file):
        copy(file,os.path.join(self.config['file']['temp_result'],os.path.basename(file)))
        os.remove(file)
    else:
        logger.error(f"The file {file} does not exist")
