from __future__ import annotations

class ChordError(Exception):
    code = "chord_error"
    user_message = "An application error occurred."

    def to_dict(self, debug: bool = False) -> dict:
        payload = {
            "ok": False,
            "error_code": self.code,
            "message": self.user_message,
        }
        if debug:
            payload["debug_detail"] = str(self)
        return payload

class ValidationError(ChordError):
    code = "validation_error"
    user_message = "Input validation failed."

class NotFoundError(ChordError):
    code = "not_found"
    user_message = "Requested item was not found."

class PipelineStateError(ChordError):
    code = "pipeline_state_error"
    user_message = "The run is not in a valid state for this operation."

class ExportError(ChordError):
    code = "export_error"
    user_message = "Export could not be completed."
