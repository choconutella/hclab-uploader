from sqlalchemy.exc import SQLAlchemyError
def save_log(engine:object, lno:str, phone:str, status:str, log:str):

    sql = '''
        insert into sine_email_log (email_date, email_tno, email_to, email_log, email_status)
        select sysdate, :lno, :phone, :message, :status from dual
    '''
    params = {'lno' : lno, 'phone' : phone, 'message': log, 'status' : status}


    try:
      with engine.connect() as conn:
        conn.execute(sql,params)
    except SQLAlchemyError as e:
      raise ValueError(f'Saving log {lno} failed. {e}')