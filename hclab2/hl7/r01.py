import configparser

class R01:
  
  def __init__(self, file):

    lines = configparser.ConfigParser(interpolation=None)
    lines.read(file)
        
    #OBR section
    obr = lines['OBR']
    self.pid  = obr['pid']
    self.apid = obr['apid'] if lines.has_option('OBR','apid') else ''
    self.pname = obr['pname']
    self.ptype = obr['ptype'] if lines.has_option('OBR','ptype') else ''
    self.birth_dt = obr['birth_dt'] if lines.has_option('OBR','birth_dt') else ''
    self.sex = obr['sex'] if lines.has_option('OBR','sex') else ''
    self.ono = obr['ono']
    self.lno = obr['lno']
    self.request_dt = obr['request_dt']
    self.specimen_dt = obr['specimen_dt'] if lines.has_option('OBR','specimen_dt') else ''
    self.specimen = obr['specimen'] if lines.has_option('OBR','specimen') else ''
    self.source = obr['source']
    self.source_cd = self.source.split('^')[0]
    self.source_nm = self.source.split('^')[1]
    self.clinician = obr['clinician']
    self.clinician_cd = self.clinician.split('^')[0]
    self.clinician_nm = self.clinician.split('^')[1]
    self.priority = obr['priority'] if lines.has_option('OBR','priority') else ''
    self.pstatus = obr['pstatus'] if lines.has_option('OBR','pstatus') else ''
    self.visitno = obr['visitno'] if lines.has_option('OBR','visitno') else ''
    self.comment = obr['comment'] if lines.has_option('OBR','comment') else ''
    self.site_id = obr['site_id'] if lines.has_option('OBR','site_id') else ''
    self.order_testid = obr['order_testid'].split('^')[0]
    self.order_testnm = obr['order_testid'].split('^')[1]
    self.obx = lines['OBX']


  def parse_obx(self, obx):

    parse = obx.split('|')

    return {
      'test_cd' : parse[0],
      'test_nm' : parse[1],
      'data_type' : parse[2],
      'result_value' : parse[3],
      'unit' : parse[4],
      'flag' : parse[5],
      'ref_range' : parse[6],
      'status' : parse[7],
      'test_comment' : parse[8]
    }