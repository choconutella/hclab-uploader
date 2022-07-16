from dataclasses import dataclass, field
from sqlalchemy.exc import SQLAlchemyError

@dataclass
class _Id:
  engine:object
  lno:str
  test_cd:str

class CheckIn(_Id):

  def __init__(self, conn:object, lno:str, test_cd:str):
    super().__init__(conn,lno,test_cd)

    self.keys = ['type_cd', 'type_nm', 'on', 'by_cd', 'by_nm']

  def get(self)->dict:
    
    sql = '''
      select os_spl_type, st_name, to_char(os_spl_rcvdt,'yyyymmddhh24miss'), os_update_by, user_name
      from ord_spl
      join ord_dtl on os_tno = od_tno and os_spl_type = od_spl_type
      join user_account on os_update_by = user_id
      join sample_type on st_code = os_spl_type
      where os_tno = :lno and od_testcode = :test_cd 
    '''
    params = {'lno' : self.lno, 'test_cd' : self.test_cd}
    
    try:
      with self.engine.connect() as conn:
        record = conn.execute(sql,params).fetchone()
    except SQLAlchemyError as e:
      raise Exception(e)

    if record is None:
      print(f'{self.lno} - {self.test_cd} check-in data can not retrieved')
      return {self.keys[i]:'' for i in range(len(self.keys))}
    
    return {self.keys[i]:record[i] if not record[i] is None else '' for i in range(len(record))}


class Validate(_Id):

  def __init__(self, conn:object, lno:str, test_cd:str):
    super().__init__(conn, lno, test_cd)
    self.keys = ['release_by_cd', 'release_by_nm', 'release_on', 'authorise_by_cd', 'authorise_by_nm', 'authorise_on']

  def get(self):
    
    sql = '''
      select od_validate_by, (select user_name from user_account where user_id = od_validate_by), to_char(od_validate_on,'yyyymmddhh24miss'),
      od_update_by, (select user_name from user_account where user_id = od_update_by), to_char(od_update_on, 'yyyymmddhh24miss')
      from ord_dtl
      where od_tno = :lno and od_testcode = :test_cd
    '''
    params = {'lno' : self.lno, 'test_cd' : self.test_cd}

    try:
      with self.engine.connect() as conn:
        record = conn.execute(sql,params).fetchone()
    except SQLAlchemyError as e:
      raise Exception(e)
    
    if record is None:
      print(f'{self.lno} - {self.test_cd} validate data cannot retrieved')
      return {self.keys[i]:'' for i in range(len(self.keys))}
      
    return {self.keys[i]:record[i] if not record[i] is None else '' for i in range(len(record))}



class Phone(_Id):

  def __init__(self, conn, lno, test_cd):
    super().__init__(conn, lno, test_cd)
    self.keys = {'by_cd', 'by_nm', 'on', 'to', 'note'}

  def get(self):
    
    sql = '''
      select tq_tel_by, user_name, to_char(tq_date,'yyyymmddhh24miss'), tq_tel_to, tq_comment 
      from telephone_queue 
      join user_account on user_id = tq_tel_by
      where tq_lab_tno = :lno and tq_testcode = :test_cd
    '''
    params = {'lno' : self.lno, 'test_cd' : self.test_cd}

    try:
      with self.engine.connect() as conn:
        record = conn.execute(sql,params).fetchone()
    except SQLAlchemyError as e:
      raise Exception(e)

    if record is None:
      return {self.keys[i]:'' for i in range(len(self.keys))}

    return {self.keys[i]:record[i] if not record[i] is None else '' for i in range(len(record))}


@dataclass
class Result:

  conn:object
  lno:str
  ono:str
  seqno:str
  test_cd:str
  test_nm:str
  data_type:str
  result_value:str
  result_ft:str
  ref_range:str
  unit:str
  flag:str
  status:str
  test_comment:str
  disp_seq:str
  order_testid:str
  order_testnm:str
  test_group:str
  item_parent:str
  his_detail:str = field(default='')
  his_header:str = field(default='')
  specimen:dict = field(init=False)
  validate:dict = field(init=False)
  phone:dict = field(init=False)
  method:str = field(init=False)

  def __post_init__(self):
    self.specimen = CheckIn(self.conn, self.lno, self.test_cd).get()
    self.validate = Validate(self.conn, self.lno, self.test_cd).get()
    self.phone = Phone(self.conn, self.lno, self.test_cd).get()
  

