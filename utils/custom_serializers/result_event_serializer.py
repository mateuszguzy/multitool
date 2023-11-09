import json
import uuid

from utils.custom_dataclasses import ResultEvent


class ResultEventSerializer(json.JSONEncoder):
    def default(self, obj: ResultEvent):
        if isinstance(obj, ResultEvent):
            return {
                "id": obj.id.__str__(),
                "source_module": obj.source_module,
                "target": obj.target,
                "result": obj.result,
            }
        else:
            return json.JSONEncoder.default(self, obj)


def result_event_decoder(data: dict) -> ResultEvent:
    return ResultEvent(
        id=uuid.uuid4(),
        source_module=data["source_module"],
        target=data["target"],
        result=data["result"],
    )


def result_event_encoder(obj: ResultEvent) -> str:
    return json.dumps(obj, cls=ResultEventSerializer)


def result_event_data_load(obj: str) -> ResultEvent:
    return json.loads(obj, object_hook=result_event_decoder)
