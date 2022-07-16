import time 
import os
from shutil import copy
import queue
from datetime import datetime
from pprint import pprint
import requests

from hclab2.hl7.r01 import R01
from hclab2.item import Item
from hclab2.bridge.result import Result
from hclab2.log import setup_logger
from services.service import Service


today = datetime.today().strftime("%Y%m%d")
logger = setup_logger("result", f"result_{today}")

class TableResult (Service):

  def __init__(self, config, hclabConnection, hisConnection):
    super(TableResult, self).__init__()
    self.message = queue.LifoQueue()
    self.config = config
    self.hclabConnection = hclabConnection
    self.hisConnection = hisConnection

  def run(self):

    time.sleep(1)    

    while self._runner.is_set():

      self._stopper.wait()

      for filename in os.listdir(self.config['file']['hl7_out']):
        file = os.path.join(self.config['file']['hl7_out'],filename)
        if os.path.isdir(file):
          pass
        else:
          if file.endswith('.R01'):
            self.message.put(f"Processing {filename}")
            logger.info(f"Processing {filename}")
            try:
              self.__process(file)

            except ValueError as error:
              logger.error(error)
              self.message.put(error)

              copy(file,os.path.join(self.config['file']['err_result'],os.path.basename(file)))
              os.remove(file)
              continue

          else:
            os.remove(file)

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

      # print(f"{r01.ono} - {obx['test_cd']} status : {obx['status']}")

      if obx['test_cd'] == 'MBFTR':
        obx.update(test_cd = r01.order_testid, test_nm = r01.order_testnm)

      item = Item(self.hclabConnection, obx['test_cd'], r01.lno)

      disp_seq = f'{item.group_seq}_{item.seq}_{("000"+str(counter))[-3:]}' 

      # save detail
      result = Result(
        self.hclabConnection,
        r01.lno,
        r01.ono,
        str(counter),
        obx['test_cd'],
        obx['test_nm'],
        obx['data_type'],
        obx['result_value'],
        obx['result_value'],
        obx['ref_range'],
        obx['unit'],
        obx['flag'],
        obx['status'],
        obx['test_comment'],
        disp_seq,
        r01.order_testid,
        r01.order_testnm,
        '',
        item.parent,
        '',
        ''
      )
      # authorise_on = yyyymmddhh24miss
      authorise_date = result.validate['authorise_on'][:8]
      authorise_time = result.validate['authorise_on'][8:14]
      header, detail = self.get_result_mapping_code(self.hclabConnection, r01.ono, obx['test_cd'])

      headers = {
        'Api-User' : self.config['api']['user'],
        'Api-Key' : self.config['api']['key']
      }
      payload = {
        'ONO' : r01.ono,
        'kd_jns_prw' : header,
        'tgl_periksa': authorise_date[:4]+'-'+authorise_date[4:6]+'-'+authorise_date[6:8],
        'jam':  authorise_time[:2]+':'+authorise_time[2:4]+':'+authorise_time[4:6],
        'id_template': detail,
        'nilai':obx['result_value'],
        'nilai_rujukan':obx['ref_range'],
        'keterangan':obx['test_comment']
      }

      logger.info(f"Send payload : \n{payload}")
      # pprint(payload)
      try:
        response = requests.post(self.config['api']['base_url']+'/api/lis/insert_result.php', headers=headers, json=payload)
      except ValueError as e:
        self.message.put(f"Cannot POST payload")

      logger.info(f"Response : \n{response.json()}")
      # pprint(response.json())

      if response.status_code != 200:
        self.message.put(f"Status Code {response.status_code}. Failed to sent result. ")
        
      
      counter += 1


    if os.path.exists(file):
        copy(file,os.path.join(self.config['file']['temp_result'],os.path.basename(file)))
        os.remove(file)
    else:
        logger.error(f"File {os.path.basename(file)} already existsdoes not exist")
      


  def get_result_mapping_code(self, ono:str, order_testid:str, test_cd:str)->dict:

    sql = """
      select tm_his_parent, tm_his_code
      from test_mapping_res
      join lisorders_dtl on his_cd = tm_his_parent
      where ono = :ono and lis_cd = :order_testid and tm_ti_code = :test_cd
    """
    params = {'ono' : ono, 'order_testid' : order_testid, 'tm_ti_code' : test_cd}

    try:
      with self.hclabConnection.connect() as conn:
        record = conn.execute(sql, params).fetchone()
    except ValueError as e:
      logger.error(f'Get mapping code of {test_cd} in {ono} failed')
    
    if record is None :
      return '',''

    return record[0], record[1]

          
