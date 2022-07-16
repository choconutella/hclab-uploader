from sqlalchemy.exc import SQLAlchemyError

def delete_row(engine:object, id:int):

  sql = 'delete from dbo."Order" where id = ?'
  params = (id)

  try:
    with engine.connect() as conn:
      conn.execute(sql, params)
  
  except SQLAlchemyError as e:
    raise Exception(f'Cannot connect HIS table while deleting id {id}. {e}')
