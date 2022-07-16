from sqlalchemy.exc import SQLAlchemyError

def insert(engine:object, result:object, site:str):
  sql = '''
    insert into ResultHd
    (
      id, pid, apid, pname, ono, lno, request_dt, source_cd, source_nm, 
      clinician_cd, clinician_nm, priority, comment, visitno, 
      orgcd, createddate
    )
    select
    ?,?,?,?,?,?,?,?,?,
    ?,?,?,?,?,
    ?, getdate()
    where not exists(select 1 from ResultHd where ono=? and orgcd=?)
  '''
  params = (
    result.ono,result.pid,result.apid,result.pname,result.ono,result.lno,result.request_dt,result.source_cd,result.source_nm,
    result.clinician_cd,result.clinician_nm,result.priority,result.comment,result.visitno,
    site,
    result.ono,site
  )
  
  try:
    with engine.connect() as conn:
      conn.execute(sql,params)
  except SQLAlchemyError as e:
    raise ValueError(f'The header of lab No. {result.lno} cannot be inserted. {e}')

def update(engine:object, result:object, site:str):
  sql = '''
    update ResultHd set
    pid=?, apid=?, pname=?, request_dt=?, source_cd=?, source_nm=?,
    clinician_cd=?, clinician_nm=?, priority=?, comment=?, visitno=?
    where ono=? and orgcd=?
  '''

  params = (
    result.pid,result.apid,result.pname,result.request_dt,result.source_cd,result.source_nm,
    result.clinician_cd,result.clinician_nm,result.priority,result.comment,result.visitno,
    result.ono,site
  )

  try:

    with engine.connect() as conn:
      conn.execute(sql,params)

  except SQLAlchemyError as e:
    raise ValueError(f'The header of Lab No. {result.lno} cannot be updated. {e}')


def save_header(engine:object, result:object, site:str):
  
  update(engine, result, site)
  insert(engine, result, site)