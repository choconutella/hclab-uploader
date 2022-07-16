from dataclasses import dataclass, field
from sqlalchemy.exc import SQLAlchemyError

@dataclass
class Item:
  engine:object
  code:str
  is_map:bool = field(default=False)
  lno:str = field(default='')
  name:str = field(init=False, default='')
  seq:str = field(init=False, default='000')
  parent:str = field(init=False, default='000000')
  group_code:str = field(init=False)
  group_name:str = field(init=False)
  group_seq:str = field(init=False, default='000')
  method:str = field(init=False)
  

  def __post_init__(self):
    self.detail()


  def get_mapping(self):

    sql = 'select tm_his_code, tm_ti_code from test_mapping where tm_ti_code=:code'

    if self.is_map:
      sql = 'select tm_his_code, tm_ti_code from test_mapping where tm_his_code=:code'

    params = {'code' : self.code}

    try:
      with self.engine.connect() as conn:
        record = conn.execute(sql,params).fetchone()
    except SQLAlchemyError as e:
      raise Exception(e)

    if record is None:
      return {'his_code' : self.code, 'lis_code' : None}
    
    return {
      'his_code' : record[0],
      'lis_code' : record[1]
    }


  def detail(self):

    if self.lno == '':
      return

    sql = '''
        select ti_name, substr('000'||ti_disp_seq,-3), od_item_parent, od_test_grp, tg_name, substr('000'||tg_ls_code,-3), ti_tm_code
        from ord_dtl 
        join test_group on od_test_grp = tg_code
        join test_item on ti_code = od_order_ti
        where od_testcode = :code and od_tno = :lno
      '''
    params = {'code':self.code, 'lno' : self.lno}

    try:
      with self.engine.connect() as conn:
        record = conn.execute(sql,params).fetchone()
    except SQLAlchemyError as e:
      raise Exception(e)
    
    if record is None:
      raise ValueError(f'{self.lno} - {self.code} detail not found')
    
    self.item_name = record[0]
    self.item_seq = record[1]
    self.item_parent = record[2]
    self.group_code = record[3]
    self.group_name = record[4]
    self.group_seq = record[5]
    self.method = record[6]

