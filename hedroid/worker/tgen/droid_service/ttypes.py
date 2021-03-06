#
# Autogenerated by Thrift Compiler (0.9.0)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py
#

from thrift.Thrift import TType, TMessageType, TException, TApplicationException

from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol, TProtocol
try:
  from thrift.protocol import fastbinary
except:
  fastbinary = None


class ErrCode:
  DEFAULT = 0
  NO_DROIDS_AVAILABLE = 1

  _VALUES_TO_NAMES = {
    0: "DEFAULT",
    1: "NO_DROIDS_AVAILABLE",
  }

  _NAMES_TO_VALUES = {
    "DEFAULT": 0,
    "NO_DROIDS_AVAILABLE": 1,
  }


class ConnParams:
  """
  Attributes:
   - host
   - port
   - password
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'host', None, None, ), # 1
    (2, TType.STRING, 'port', None, None, ), # 2
    (3, TType.STRING, 'password', None, None, ), # 3
  )

  def __init__(self, host=None, port=None, password=None,):
    self.host = host
    self.port = port
    self.password = password

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.host = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.port = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.STRING:
          self.password = iprot.readString();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('ConnParams')
    if self.host is not None:
      oprot.writeFieldBegin('host', TType.STRING, 1)
      oprot.writeString(self.host)
      oprot.writeFieldEnd()
    if self.port is not None:
      oprot.writeFieldBegin('port', TType.STRING, 2)
      oprot.writeString(self.port)
      oprot.writeFieldEnd()
    if self.password is not None:
      oprot.writeFieldBegin('password', TType.STRING, 3)
      oprot.writeString(self.password)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class ApplicationException(TException):
  """
  Attributes:
   - msg
   - code
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'msg', None, None, ), # 1
    (2, TType.I32, 'code', None, 0, ), # 2
  )

  def __init__(self, msg=None, code=thrift_spec[2][4],):
    self.msg = msg
    self.code = code

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.msg = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.I32:
          self.code = iprot.readI32();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('ApplicationException')
    if self.msg is not None:
      oprot.writeFieldBegin('msg', TType.STRING, 1)
      oprot.writeString(self.msg)
      oprot.writeFieldEnd()
    if self.code is not None:
      oprot.writeFieldBegin('code', TType.I32, 2)
      oprot.writeI32(self.code)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __str__(self):
    return repr(self)

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)
