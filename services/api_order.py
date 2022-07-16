import time 
import queue
import requests
from pprint import pprint
from datetime import datetime
from hclab2.bridge.order import Order
from hclab2.item import Item
from hclab2.log import setup_logger
from services.service import Service

today = datetime.today().strftime("%Y%m%d")
logger = setup_logger("order", f"order_{today}")


class TableOrder(Service):

  def __init__(self, config, hclabConnection, hisConnection):
    super(TableOrder, self).__init__()
    self.message = queue.LifoQueue()
    self.config = config
    self.hclabConnection = hclabConnection
    self.hisConnection = hisConnection

  def run(self):
    
    time.sleep(3)

    logger.info("Stating order thread")

    while self._runner.is_set():

      if self._stopper.is_set():
        logger.info("Thread stopped")

      self._stopper.wait()

      try: 
        self.__process()
      
      except ValueError as error:
        logger.error(error)
        self.message.put(error)
        continue

      time.sleep(5) 


  def __process(self):
    '''Order will be generated to text file and insert into LISOrder table'''

    headers = {
      'Api-User' : self.config['api']['user'],
      'Api-Key' : self.config['api']['key']
    }
    
    try:
      response = requests.get(self.config['api']['base_url']+'/api/lis/get_order.php', headers=headers)
    except ValueError as e:
      raise ValueError(f'Cannot retrieve order. {e}')

    logger.info(f"Response : \n{response.json()}")

    if response.status_code != 200:
      raise ValueError(f'Response from API not returning order. {response.json()}')
      
    context = response.json()
    order_control = 'NW'
    
    for record in context['data']:
      
      logger.info(f"Processing ONO {record['ono']}")

      order = Order(
        record['request_dt'][:4]+record['request_dt'][5:7]+record['request_dt'][8:10]+'000000',
        order_control,
        '0',
        record['pname'],
        record['pid'] if 'pid' in record else '00',
        record['sex'] if 'sex' in record else '0',
        record['birth_dt'],
        {
          1: record['address1'] if 'address1' in record else '', 
          2: record['address2'] if 'address2' in record else '', 
          3: record['address3'] if 'address3' in record else '', 
          4: record['address4'] if 'address4' in record else ''
        },
        record['ptype'] if 'ptype' in record else '00',
        record['ono'],
        record['request_dt'][:4]+record['request_dt'][5:7]+record['request_dt'][8:10]+'000000',
          {
            'code' : record['clinician_cd'],
            'name' : record['clinician_nm']
          },
          {
            'code' : record['source_cd'],
            'name' : record['source_nm']
          },
          record['visitno'] if 'visitno' in record else '',
          record['priority'],
          record['pstatus'] if 'pstatus' in record else '',
          record['comment'] if 'comment' in record else '',
          record['order_testid']
      )

      try:
        order.save_lisorder(self.hclabConnection)
      except ValueError as e:
        logger.error("Fail saving to LISOrder")

      logger.info("Create A04")
      order.createA04(self.config['file']['hl7_in'], self.config['file']['temp_msg'])
      
      mapped_tests = set()

      if not record['order_testid'] is None:
        tests = [t for t in record['order_testid'].split('~')]
        for test in tests:

          map = Item(self.hclabConnection, test, is_map=True).get_mapping()
          if map['lis_code'] is None:
            logger.warning(f"HIS Code {test} not found")
            mapped_test = ''
          else:
            mapped_test = Item(self.hclabConnection, test, is_map=True).get_mapping()['lis_code']
            
          mapped_tests.add(mapped_test)

          # save to lisorders_dtl

          try:
            self.save_lisorder_detail(self.hclabConnection, record['ono'], test, mapped_test)
          except ValueError as e:
            logger.error("Fail saving to lisorders_dtl")

      order.tests = '~'.join(mapped_tests)

      try:
        order.createO01(self.config['file']['hl7_in'], self.config['file']['temp_msg'])
      except ValueError as e:
        logger.error("Fail creating O01")

      # DELETE / UPDATE FLAG HERE
      headers = {
        'Api-User' : self.config['api']['user'],
        'Api-Key' : self.config['api']['key']
      }
      payload = {
        'ONO' : record['ono']
      }

      logger.info(f"Updating order flag ONO {record['ono']}")
      pprint(payload)
      try:
        response = requests.get(self.config['api']['base_url']+'/api/lis/return_order.php', headers=headers, json=payload)
      except ValueError as e:
        raise ValueError(f'Cannot update order confirmation. {e}')

      if response.status_code != 200:
        raise ValueError(f'Failed to sent confirmation order to API. {response.json()}')
        

  
  def save_lisorder_detail(self, ono:str, his:str, lis:str):

    sql = """
      insert into lisorders_dtl(ono, his_cd, lis_cd) select :ono, :his, :lis from dual 
      where not exists (select 1 from lisorders_dtl where ono = :ono and his_cd = :his)
    """
    params = {'ono' : ono, 'his' : his, 'lis' : lis }

    try:
      with self.hclabConnection.connect() as conn:
        conn.execute(sql, params)
    except ValueError as e:
      print(f'Insert {ono} - {his} - {lis} into lisorders_dtl failed')

