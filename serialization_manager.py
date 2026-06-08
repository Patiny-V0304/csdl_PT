import json
import xml.etree.ElementTree as ET
from dataset_generator import SyncRecord 

#import Protobuf
try:
    import sync_schema_pb2
    PROTOBUF_AVAILABLE = True
except ImportError:
    PROTOBUF_AVAILABLE = False
    print("Lưu ý: Chưa tìm thấy sync_schema_pb2.py. Vui lòng compile file .proto.")

class FormatConverter:
    # 1. JSON IMPLEMENTATION
    @staticmethod
    def json_serialize(dataset):
        # Chuyển Object thành Dictionary để ép sang JSON
        dict_list = []
        for obj in dataset:
            dict_list.append({
                "global_oid": obj.global_oid,
                "record_id": obj.record_id,
                "metadata": obj.metadata,
                "trust_score": obj.trust_score,
                "history_logs": obj.history_logs
            })
        # Trả về dạng byte để truyền qua mạng (Network Throughput)
        return json.dumps(dict_list).encode('utf-8')

    @staticmethod
    def json_rehydrate(byte_data):
        # Giải tuần tự hóa & Tái tạo (Rehydration) lại thành Object thực
        data = json.loads(byte_data.decode('utf-8'))
        rehydrated_objects = []
        for item in data:
            obj = SyncRecord(item['record_id'], item['metadata'])
            obj.global_oid = item['global_oid'] # Giữ nguyên OID cũ
            obj.trust_score = item['trust_score']
            obj.history_logs = item['history_logs']
            rehydrated_objects.append(obj)
        return rehydrated_objects

    # 2. XML IMPLEMENTATION
    @staticmethod
    def xml_serialize(dataset):
        root = ET.Element("Dataset")
        for obj in dataset:
            record_elem = ET.SubElement(root, "SyncRecord")
            ET.SubElement(record_elem, "global_oid").text = str(obj.global_oid)
            ET.SubElement(record_elem, "record_id").text = str(obj.record_id)
            ET.SubElement(record_elem, "metadata").text = obj.metadata
            ET.SubElement(record_elem, "trust_score").text = str(obj.trust_score)
            
            logs_elem = ET.SubElement(record_elem, "history_logs")
            for log in obj.history_logs:
                log_node = ET.SubElement(logs_elem, "log")
                ET.SubElement(log_node, "event_id").text = str(log["event_id"])
                ET.SubElement(log_node, "status").text = log["status"]
                
        return ET.tostring(root, encoding='utf-8')

    @staticmethod
    def xml_rehydrate(byte_data):
        root = ET.fromstring(byte_data)
        rehydrated_objects = []
        for record_elem in root.findall('SyncRecord'):
            record_id = int(record_elem.find('record_id').text)
            metadata = record_elem.find('metadata').text
            
            obj = SyncRecord(record_id, metadata)
            obj.global_oid = record_elem.find('global_oid').text
            obj.trust_score = float(record_elem.find('trust_score').text)
            
            logs = []
            for log_node in record_elem.find('history_logs').findall('log'):
                logs.append({
                    "event_id": int(log_node.find('event_id').text),
                    "status": log_node.find('status').text
                })
            obj.history_logs = logs
            rehydrated_objects.append(obj)
        return rehydrated_objects

    # 3. PROTOCOL BUFFERS (BINARY) IMPLEMENTATION
    @staticmethod
    def protobuf_serialize(dataset):
        if not PROTOBUF_AVAILABLE:
            return b""
        
        dataset_msg = sync_schema_pb2.DatasetMsg()
        for obj in dataset:
            record_msg = dataset_msg.records.add()
            record_msg.global_oid = obj.global_oid
            record_msg.record_id = obj.record_id
            record_msg.metadata = obj.metadata
            record_msg.trust_score = obj.trust_score
            
            for log in obj.history_logs:
                log_msg = record_msg.history_logs.add()
                log_msg.event_id = log["event_id"]
                log_msg.status = log["status"]
                
        return dataset_msg.SerializeToString() # Đã là nhị phân (bytes)

    @staticmethod
    def protobuf_rehydrate(byte_data):
        if not PROTOBUF_AVAILABLE:
            return []
            
        dataset_msg = sync_schema_pb2.DatasetMsg()
        dataset_msg.ParseFromString(byte_data)
        
        rehydrated_objects = []
        for record_msg in dataset_msg.records:
            obj = SyncRecord(record_msg.record_id, record_msg.metadata)
            obj.global_oid = record_msg.global_oid
            obj.trust_score = record_msg.trust_score
            
            logs = []
            for log_msg in record_msg.history_logs:
                logs.append({
                    "event_id": log_msg.event_id,
                    "status": log_msg.status
                })
            obj.history_logs = logs
            rehydrated_objects.append(obj)
            
        return rehydrated_objects