from sqlalchemy.exc import SQLAlchemyError

def select(engine:object, site:str)->list:
  '''
  Returns list of order from HIS table

  Parameters:
    engine : object
        Connection to HIS database
    
    site : str
        Site code
  '''
  
  sql = """
    select id, 
    message_dt,
    ono,
    order_control,
    pid,
    apid,
    pname,
    address1, address2, address3, address4,
    ptype,
    birth_dt,
    sex,
    '' as lno,
    request_dt,
    source,
    clinician,
    room_no,
    priority,
    '' as pstatus,
    comment,
    visitno,
    order_testid,
    address4 as email
    from dbo."Order" where OrganizationCode = ?
  """
  param = (site)
  try:
    with engine.connect() as conn:
        records = conn.execute(sql,param).fetchall()

  except SQLAlchemyError as e:
    raise Exception(f'HIS Database not found. {e}')

  return records