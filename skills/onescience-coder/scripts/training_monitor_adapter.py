"""Optional OneScience integration. Copy alongside the generated trainer.

Only monitoring operations belong in the factory/calls below. Model creation,
data loading, forward/backward and optimizer updates remain in the trainer.
"""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import sys
import tempfile


class OptionalTrainingMonitor:
    def __init__(self, factory):
        self.monitor = None
        self.reason = None
        self._warnings = set()
        if os.environ.get("ONECODE_MONITORING_DISABLED") == "1":
            self._warn("monitoring_preparation_unavailable")
            return
        try:
            self.monitor = factory()
            if getattr(self.monitor, "config", None) is None:
                self._warn("onescience_monitor_disabled")
                self.monitor = None
            elif getattr(self.monitor, "initialization_error", None):
                self._warn("monitoring_initialization_failed")
                self._call("close")
                self.monitor = None
        except Exception as error:
            self._warn("monitoring_initialization_failed", error)

    def _warn(self, code, error=None):
        # Exception messages may contain paths/credentials; report only the type.
        self.reason = code
        if code in self._warnings:
            return
        self._warnings.add(code)
        try:
            print("ONECODE_MONITORING_WARNING " + json.dumps({
                "code": code, "error_type": type(error).__name__ if error else None,
                "training_continues": True,
            }), file=sys.stderr, flush=True)
        except Exception:
            pass

    def _call(self, name, *args, **kwargs):
        if self.monitor is None:
            return False if name == "is_enabled" else None
        try:
            return getattr(self.monitor, name)(*args, **kwargs)
        except Exception as error:
            self._warn("monitoring_operation_failed", error)
            return False if name == "is_enabled" else None

    def __getattr__(self, name):
        if name not in {"is_enabled", "start_phase", "end_phase", "record_train", "record_validation",
                        "capture_gradients", "reenable", "configure", "poll_config", "flush",
                        "status", "state_dict", "load_state_dict"}:
            raise AttributeError(name)
        return lambda *args, **kwargs: self._call(name, *args, **kwargs)

    @contextmanager
    def stage(self, name):
        stage = self._call("stage", name)
        entered = False
        if stage is not None:
            try:
                stage.__enter__()
                entered = True
            except Exception as error:
                self._warn("monitoring_stage_failed", error)
        # Never catch errors from the training body or suppress its exception.
        try:
            yield
        finally:
            if entered:
                try:
                    stage.__exit__(None, None, None)
                except Exception as error:
                    self._warn("monitoring_stage_close_failed", error)

    def publish_runtime(self, event_root, title):
        if self.monitor is None or os.environ.get("RANK", "0") != "0":
            return False
        required = ["ONECODE_TASK_ID", "ONECODE_RUN_ID", "ONECODE_ATTEMPT_ID",
                    "ONECODE_EXECUTION_TARGET", "ONECODE_RUNTIME_MANIFEST"]
        if not all(os.environ.get(key, "").strip() for key in required):
            self._warn("platform_identity_unavailable")
            return False
        temporary = None
        try:
            config = self.monitor.config
            if (config.run_id != os.environ["ONECODE_RUN_ID"] or
                    config.attempt_id != os.environ["ONECODE_ATTEMPT_ID"]):
                raise ValueError("monitor identity differs from platform identity")
            target = Path(os.environ["ONECODE_RUNTIME_MANIFEST"])
            if not target.is_absolute() or not Path(event_root).is_absolute():
                raise ValueError("absolute runtime/event paths required")
            event = {"schema": "onecode.training/v1", "kind": "training", "title": title,
                     "taskId": os.environ["ONECODE_TASK_ID"], "runId": os.environ["ONECODE_RUN_ID"],
                     "attemptId": os.environ["ONECODE_ATTEMPT_ID"],
                     "executionTargetRef": os.environ["ONECODE_EXECUTION_TARGET"],
                     "eventRoot": str(Path(event_root).resolve())}
            if os.environ.get("ONECODE_REGION"):
                event["region"] = os.environ["ONECODE_REGION"]
            if os.environ.get("SLURM_JOB_ID"):
                event.update(jobRef=os.environ["SLURM_JOB_ID"], scheduler="slurm")
            target.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(mode="w", dir=target.parent, delete=False) as stream:
                temporary = stream.name
                json.dump(event, stream)
            os.replace(temporary, target)
            return True
        except Exception as error:
            self._warn("monitoring_runtime_publication_failed", error)
            return False
        finally:
            if temporary:
                try:
                    Path(temporary).unlink(missing_ok=True)
                except Exception:
                    pass

    def close(self):
        result = self._call("close")
        if self.monitor is not None and (not isinstance(result, dict) or not result.get("closed")
                                         or result.get("error") or result.get("pending_records")):
            self._warn("monitoring_close_incomplete")
        return result

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False
