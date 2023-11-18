import json

from utils.custom_dataclasses import StartModuleEvent


class StartModuleEventSerializer(json.JSONEncoder):
    def default(self, obj: StartModuleEvent):
        if isinstance(obj, StartModuleEvent):
            return {
                "id": obj.id.__str__(),
                "source_module": obj.source_module,
                "destination_module": obj.destination_module,
                "target": obj.target,
                "result": obj.result,
            }
        else:
            return json.JSONEncoder.default(self, obj)


def start_module_event_decoder(data: dict) -> StartModuleEvent:
    return StartModuleEvent(
        id=data["id"],
        source_module=data["source_module"],
        destination_module=data["destination_module"],
        target=data["target"],
        result=data["result"],
    )


def start_module_event_encoder(obj: StartModuleEvent) -> str:
    return json.dumps(obj, cls=StartModuleEventSerializer)


def start_module_event_data_load(obj: str) -> StartModuleEvent:
    return json.loads(obj, object_hook=start_module_event_decoder)
