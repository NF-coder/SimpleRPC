class SOTServer(): # 
    def __init__(self, proto: str, pb2_grpc, pb2):
        super(pb2_grpc.SOTServerServicer)
        self.proto = proto
        self.SOTServer_pb2 = pb2

    def get_active_proto(self, *args, **kwargs):
        return self.SOTServer_pb2.get_active_protoResponce(proto=self.proto)