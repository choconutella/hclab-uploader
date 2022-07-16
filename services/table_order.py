import time 
import queue
import sqlalchemy as db
from datetime import datetime
from hclab2.bridge.order import Order
from hclab2.item import Item
from hclab2.log import setup_logger
from query.get_order import select
from query.delete_order import delete_row
from services.service import Service

today = datetime.today().strftime("%Y%m%d")
logger = setup_logger("order", f"order_{today}")

class TableOrder(Service):

  def __init__(self, config):
    super(TableOrder, self).__init__()
    self.message = queue.LifoQueue()
    self.config = config

    ora = config['hclab']
    self.hclabConnection = db.create_engine(f"oracle://{ora['user']}:{ora['pass']}@{ora['host']}:{ora['port']}/{ora['db']}")

    his = config['his']
    self.hisConnection = db.create_engine(f"mssql+pyodbc://{his['user']}:{his['pass']}@{his['dsn']}")

  def run(self):
    
    time.sleep(1)

    logger.info("Order thread is running...")

    while self._runner.is_set():

      try: 
        print("From Order")
        # self.__process()
      
      except ValueError as error:
        logger.error(error)
        self.message.put(error)
        continue

      time.sleep(5) 


  def __process(self):
    '''
    Order will be generated to text file and insert into LISOrder table
    '''

    records = select(self.hisConnection, self.config['his']['site'])

    for record in records:
      clinician_cd = record['clinician'].split('^')[0] if not record['clinician'] is None else '00'
      clinician_nm = record['clinician'].split('^')[1] if not record['clinician'] is None else 'N/A'

      source_cd = record['source'].split('^')[0] if not record['source'] is None else '00'
      source_nm = record['source'].split('^')[1] if not record['source'] is None else 'N/A'

      order = Order(
        record['id'],
        record['message_dt'],
        record['order_control'],
        '0',
        record['pname'],
        record['pid'] if not record['pid'] is None else '00',
        record['sex'] if not record['sex'] is None else '0',
        record['birth_dt'],
        {
          1: record['address1'] if not record['address1'] is None else '', 
          2: record['address2'] if not record['address2'] is None else '', 
          3: record['address3'] if not record['address3'] is None else '', 
          4: record['address4'] if not record['address4'] is None else ''
        },
        record['ptype'],
        record['ono'],
        record['request_dt'],
        {
          'code' : clinician_cd if clinician_cd != '' else '00',
          'name' : clinician_nm if clinician_nm != '' else 'N/A'
        },
        {
          'code' : source_cd if source_cd != '' else '00',
          'name' : source_nm if source_nm != '' else 'N/A'
        },
        record['visitno'] if not record['visitno'] is None else '',
        record['priority'],
        record['pstatus'] if not record['pstatus'] is None else '',
        record['comment'] if not record['comment'] is None else '',
        record['order_testid'],
        record['room_no'],
        record['email']
      )

      order.save_lisorder(self.hclabConnection)
      order.createA04(self.config['file']['hl7_in'], self.config['file']['temp_msg'])
      
      mapped_tests = set()

      if not record['order_testid'] is None:
        tests = [t for t in record['order_testid'].split('~')]
        for test in tests:
          mapped_test = Item(self.hclabConnection, test, is_map=True).get_mapping()['lis_code']
          mapped_tests.add(mapped_test)
          print(mapped_test)
      order.tests = '~'.join(mapped_tests)
      order.createO01(self.config['file']['hl7_in'], self.config['file']['temp_msg'])

      delete_row(self.hisConnection, record['id'])