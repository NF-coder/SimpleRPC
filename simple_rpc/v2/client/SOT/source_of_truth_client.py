from .proto import sot_pb2
from .proto import sot_pb2_grpc

class SOT(sot_pb2_grpc.SOTServicer): # 
    def __init__(self, proto: str):
        self.proto = proto.split("service SOT")[0]
    
    def get_proto(self, *args, **kwargs):
        return sot_pb2.get_protoResponce(proto=self.proto)
        #return self.proto