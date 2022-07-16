from sqlalchemy.exc import SQLAlchemyError

def insert(engine:object, result:object):

  sql = '''
    insert into ResultDt
    (
      id, ono, seqno, test_cd, test_nm, data_typ, 
      result_value, result_ft, unit, flag, ref_range, status, test_comment, 
      validate_by, validate_on,
      disp_seq, order_testid, order_testnm, test_group, item_parent, orgcd, createddate
    )
    select
      ?,?,?,?,?,?,
      ?,?,?,?,?,?,?, 
      ?,?,
      ?,?,?,?,?,?, getdate()
    where not exists (select 1 from ResultDt where ono=? and test_cd=? and orgcd=?)
  '''
  params = (
    result.ono, result.ono, result.seqno, result.test_cd, result.test_nm, result.data_type,
    result.result_value, result.result_ft,result.unit,result.flag,result.ref_range,result.status,result.test_comment,
    result.validate['authorise_by_cd']+'^'+result.validate['authorise_by_nm'], result.validate['authorise_on'],
    result.disp_seq, result.order_testid,result.order_testnm,result.test_group,result.item_parent,result.site,
    result.ono,result.test_cd,result.site
  )

  try:
    with engine.connect() as conn:
      conn.execute(sql,params)
  except SQLAlchemyError as e:
    raise ValueError(f'Test {result.test_cd} of Lab No. {result.lno} cannot be inserted. {e}')


def update(engine:object, result:object):

  sql = """
    update ResultDt set
    test_nm=? , result_value=?, result_ft=?, ref_range=?, unit = ?,
    status=?, test_comment=?, 
    validate_on=?, validate_by=?,
    disp_seq=?, test_group=?
    where ono=? and test_cd=? and orgcd=?
  """
  params = (
    result.test_nm, result.result_value,result.result_ft,result.ref_range,result.unit,
    result.status, result.test_comment,
    result.validate['authorise_on'], result.validate['authorise_by_cd']+'^'+result.validate['authorise_by_nm'],
    result.disp_seq,result.test_group,
    result.ono,result.test_cd,result.site
  )

  try:
    with engine.connect() as conn:
      conn.execute(sql,params)
  except SQLAlchemyError as e:
    raise ValueError(f'Test {result.test_cd} of Lab No. {result.lno} cannot be updated. {e}')


def save_detail(engine:object, result:object):

  update(engine, result)
  insert(engine, result)