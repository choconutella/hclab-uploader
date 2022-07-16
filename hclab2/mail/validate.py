from dataclasses import dataclass

INCLUDE_TESTS = ['AG-COV', 'SARKUA', 'SCOV2P', 'COV-19']

@dataclass
class Validate():

  engine:object
  lno:str
  

  def all(self)->tuple:

    score = 0
    message = ''
    
    if not self.authorise():
      score =+ 1
      message = message + 'Not all test validated yet, '

    if not self.tests():
      score =+ 1
      message = message + 'Exclude Test Available, '
    
    if not self.sample():
      score =+ 1
      message = message + 'Rejected specimen available, '

    if not self.source():
      score =+ 1
      message = message + 'Excluded clinic available'
    
    if score == 0:
      return True, 'Success'
    
    return False, message



  def has_repeated(self,count:int)->bool:
    """Check current number already successfully sent email"""

    sql = "select count(email_tno) from sine_email_log where email_tno = :lno and email_status = 'SENT'"
    params = {'lno' : self.lno}
    
    with self.engine.connect() as conn:
      record = conn.execute(sql, params).fetchone()

    return True if record[0] >= count else False


  def pid(self)->bool:
    """Validation to check patient have valid PID"""
    
    sql = "select oh_pid from ord_hdr where oh_tno = :lno and oh_pid <> '00'"
    params = {'lno' : self.lno}

    with self.engine.connect() as conn:
      record = conn.execute(sql,params).fetchone()

    return True if not record is None else False


  def source(self)->bool:
    """Validation to check patient source"""

    sql = """
      select substr(specialty_code,2,1) 
      from ord_hdr
      join hfclinic on oh_clinic_code = clinic_code
      where oh_tno = :lno and substr(specialty_code,2,1) = 'Y'
    """
    params = {'lno' : self.lno}
    
    with self.engine.connect() as conn:
      record = conn.execute(sql, params).fetchone()
    
    return True if not record is None else False


  def tests(self)->bool:
    """Validation to check exclude test"""

    sql = "select od_testcode from ord_dtl where od_tno = :lno"
    params = {'lno' : self.lno}

    with self.engine.connect() as conn:
      records = conn.execute(sql, params).fetchall()    

    for record in records:
      if record[0] in INCLUDE_TESTS:
        return record[0]

    return False

  def authorise(self)->bool:
    """Validation to check all test already authorise"""

    sql = "select od_testcode from ord_dtl where od_tno = :lno and od_ctl_flag2 is null"
    params = {'lno' : self.lno}

    with self.engine.connect() as conn:
      records = conn.execute(sql,params).fetchall()

    return True if not records is None else False


  def sample(self)->bool:
    """Validation to check reject specimen"""

    sql = "select os_spl_type from ord_spl where os_tno = :lno and os_spl_rj_flag = 'Y'"
    params = {'lno' : self.lno}

    with self.engine.connect() as conn:
      records = conn.execute(sql, params).fetchall()
    
    return True if not records is None else False
