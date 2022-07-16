from dataclasses import dataclass, field
from sqlalchemy.exc import SQLAlchemyError

@dataclass
class Patient:

  engine:object
  lno: str = field(default='')
  pid: str = field(default='')
  site:str = field(init=False)
  trx_dt: str = field(init=False)
  apid: str = field(init=False)
  name: str = field(init=False)
  birth_dt: str = field(init=False)
  sex: str = field(init=False)
  address: dict = field(init=False)
  email: str = field(init=False)
  phone: str = field(init=False)
  ic_no: str = field(init=False)


  def __post_init__(self):
    self.get()


  def get(self):
    '''Retrieve attribute's value'''

    if self.lno == '' and self.pid == '':
      raise ValueError('LNO or PID should have a value')

    sql = '''
        select oh_pid, oh_apid, oh_last_name, to_char(oh_bod,'ddmmyy'), oh_sex, oh_pataddr1, oh_pataddr2, oh_pataddr3, oh_pataddr4,
        ic_no, dbemail, dbhphone_no, (select sid_name from site_id where sid_code = oh_ls_code), to_char(oh_trx_dt,'yyyymmdd')
        from ord_hdr
        join cust_master on oh_pid = dbcode
      '''

    if self.lno !='' :
      sql = sql + ' where oh_tno = :lno'
      params = {'lno' : self.lno}

    elif self.pid != '' :
      sql = sql + ' where oh_pid = :pid'
      params = {'pid' : self.pid}

    try:
      with self.engine.connect() as conn:
        record = conn.execute(sql,params).fetchone()
    except SQLAlchemyError as e:
      raise Exception(e)

    if record is None:
      raise ValueError(f'Patient with Lab No. / PID : {self.lno} / {self.pid} data not found')

    # ASSIGN VALUE TO ATTRIBUTES
    self.pid = record[0]
    self.apid = record[1]
    self.name = record[2]
    self.birth_dt = record[3]
    self.sex = record[4]
    self.address = {1:record[5], 2:record[6], 3:record[7], 4:record[8]}
    self.ic_no = record[9]
    self.email = record[10]
    self.phone = record[11]
    self.site = record[12]
    self.trx_dt = record[13]

    