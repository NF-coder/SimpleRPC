class SOT(): # 
    def __init__(self, proto: str, sot_pb2_grpc__, sot_pb2__):
        super(sot_pb2_grpc__.SOTServicer)
        self.proto = proto.split("service SOT")[0]
        self.sot_pb2 = sot_pb2__
    def get_proto(self, *args, **kwargs):
        return self.sot_pb2.get_protoResponce(proto=self.proto)
        #return self.proto