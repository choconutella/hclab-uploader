from dataclasses import dataclass, field
import os
from shutil import copy
from sqlalchemy.exc import SQLAlchemyError

@dataclass
class Order:
  id:int
  message_dt:str
  order_control:str
  site:str
  name:str
  pid:str
  sex:str
  birth_dt:str
  address:dict
  ptype:str
  ono:str
  request_dt:str
  clinician:dict
  source:dict
  visitno:str
  priority:str
  pstatus:str
  comment:str
  tests:str
  room_no:str = field(default='')
  email:str = field(default='')
  phone:str = field(default='')
  apid:str = field(default='')
  ic_no:str = field(default='')

  def __post_init__(self):
    pass

  def createO01(self, dest:str, backup:str):
    line = "[MSH]\n"
    line = line + "message_id=O01\n"
    line = line + f"message_dt={self.message_dt}\n"
    line = line + "version=2.3\n"
    line = line + "[OBR]\n"
    line = line + f"order_control={self.order_control}\n"
    line = line + f"site_id={self.site}\n"
    line = line + f"pid={self.pid}\n"
    line = line + f"apid={self.apid}\n"
    line = line + f"pname={self.name}\n"
    line = line + f"address={self.address[1]}^{self.address[2]}^{self.address[3]}^{self.address[4]}\n"
    line = line + f"ptype={self.ptype}\n"
    line = line + f"birth_dt={self.birth_dt}\n"
    line = line + f"sex={self.sex}\n"
    line = line + f"ono={self.ono}\n"
    line = line + f"lno=\n"
    line = line + f"request_dt={self.request_dt}\n"
    line = line + f"source={self.source['code']}^{self.source['name']}\n"
    line = line + f"clinician={self.clinician['code']}^{self.clinician['name']}\n"
    line = line + f"room_no={self.room_no}\n"
    line = line + f"priority={self.priority}\n"
    line = line + f"pstatus={self.pstatus}\n"
    line = line + f"comment={self.comment}\n"
    line = line + f"visitno={self.visitno}\n"
    line = line + f"order_testid={self.tests}\n"
    
    with open(os.path.join(backup, f"O01_{self.ono}_{self.message_dt}.txt"),'w') as f:
      f.writelines(line)
    
    copy(os.path.join(backup, f"O01_{self.ono}_{self.message_dt}.txt"),dest)

  def createA04(self, dest:str, backup:str):
    line = "[MSH]\n"
    line = line + f"message_id=A08|1006036449\n"
    line = line + f"message_dt={self.message_dt}\n"
    line = line + f"receiving_application=HCLAB\n"
    line = line + f"version=2.3\n"
    line = line + f"[PID]\n"
    line = line + f"pid={self.pid}\n"
    line = line + f"pname={self.name}\n"
    line = line + f"title=\n"
    line = line + f"apid={self.apid}\n"
    line = line + f"other_name=\n"
    line = line + f"birth_dt={self.birth_dt}\n"
    line = line + f"sex={self.sex}\n"
    line = line + f"address={self.address[1]}^^{self.address[2]}^^{self.address[3]}^{self.address[4]}\n"
    line = line + f"contact={self.phone}^^^{self.email}\n"
    line = line + f"[PV1]\n"
    line = line + f"patient_type=\n"
    line = line + f"current_loc={self.source['code']}^{self.source['name']}\n"
    line = line + f"current_room=\n"
    line = line + f"prior_loc=\n"
    line = line + f"prior_room=\n"
    line = line + f"attending_doctor={self.clinician['code']}^{self.clinician['name']}\n"
    line = line + f"visit_number=\n"
    line = line + f"date={self.message_dt[:8]}\n" 

    with open(os.path.join(backup, f"A04_{self.ono}_{self.message_dt}.txt"),'w') as f:
      f.writelines(line)


    copy(os.path.join(backup, f"A04_{self.ono}_{self.message_dt}.txt"),dest)

  def save_lisorder(self, engine:object):
    sql = """
    insert into lisorders
    (
      "id", message_dt, ono, order_control, pid, apid, pname, address, 
      ptype, birth_dt, sex, request_dt, clinician, source, room_no, priority, visitno, order_testid
    )
    values 
    (
      :id, :message_dt, :ono, :order_control, :pid, :apid, :name, :address,
      :ptype, :birth_dt, :sex, :request_dt, :clinician, :source, :room_no, :priority, :visitno, :order_testid
    )
  """
    params = {
      'id' : self.id,
      'message_dt' : self.message_dt,
      'ono' : self.ono,
      'order_control' : self.order_control,
      'pid' : self.pid,
      'apid' : self.apid,
      'name' : self.name,
      'address' : '^'.join([addr for addr in self.address.values()]),
      'ptype' : self.ptype,
      'birth_dt' : self.birth_dt,
      'sex' : self.sex,
      'request_dt' : self.request_dt,
      'clinician' : '^'.join([ c for c in self.clinician.values()]),
      'source' : '^'.join([ s for s in self.source.values()]),
      'room_no' : self.room_no,
      'priority' : self.priority,
      'visitno' : self.visitno,
      'order_testid' : self.tests
    }

    try:
      with engine.connect() as conn:
        conn.execute(sql,params)
    except SQLAlchemyError as e:
      raise Exception(f'Connecting to LISORDERS in HCLAB DB failed. {e}')
