"""Initialize OneScience first, then native TensorBoard; never retry training.

Copy alongside the trainer. Only monitoring belongs in the factory and calls;
model/data initialization and training exceptions stay in the trainer.
"""
from contextlib import contextmanager, nullcontext
import json
import math
from numbers import Real
import os
from pathlib import Path
import sys
import tempfile


class TensorBoardMonitor:
    """Basic scalar writer. Adds no distributed communication or device probes."""

    def __init__(self, output_dir, *, rank, world_size, record_every_updates, flush_secs):
        from torch.utils.tensorboard import SummaryWriter

        if record_every_updates < 1 or flush_secs <= 0:
            raise ValueError("positive monitoring cadence required")
        self.world_size, self.cadence = world_size, record_every_updates
        self.writer = SummaryWriter(str(Path(output_dir) / "tensorboard"), flush_secs=flush_secs) if rank == 0 else None
        self.closed, self.last_step = False, -1
        self.validation = None
        self.validation_step = None
        self.last_validation_step = -1

    def is_enabled(self, component=None):
        return self.writer is not None and not self.closed and component in (None, "loss", "lr", "throughput")

    def stage(self, name):
        return nullcontext()

    def start_phase(self, name, **kwargs):
        if name == "validation":
            self.validation, self.validation_step = [0.0, 0.0], None

    def _tag(self, phase, metric):
        scope = "rank_0" if self.world_size > 1 else "step"
        return f"{metric}/{phase}/{scope}/{metric}"

    def _number(self, value):
        if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
            raise ValueError("existing finite Python scalars required")
        return float(value)

    def _step(self, value):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError("nonnegative integer step required")
        return value

    def record_train(self, *, global_step, loss, update_applied=True, lr_used=(),
                     sample_count=None, elapsed_seconds=None, **kwargs):
        if not self.is_enabled() or not update_applied:
            return {"accepted": False, "reason": "disabled/no_update"}
        step = self._step(global_step)
        if step <= self.last_step:
            return {"accepted": False, "reason": "non_increasing_step"}
        values = {self._tag("train", "loss"): self._number(loss)}
        values.update({f"lr/train/group_{i}": self._number(lr) for i, lr in enumerate(lr_used)})
        if sample_count is not None and elapsed_seconds is not None:
            count, elapsed = self._number(sample_count), self._number(elapsed_seconds)
            if count < 0 or elapsed <= 0:
                raise ValueError("invalid throughput measurement")
            values[self._tag("train", "throughput")] = count / elapsed
        self.last_step = step
        if step % self.cadence:
            return {"accepted": False, "reason": "cadence"}
        for tag, value in values.items():
            self.writer.add_scalar(tag, value, step)
        return {"accepted": True}

    def record_validation(self, *, global_step, loss, loss_weight=1, **kwargs):
        if not self.is_enabled() or self.validation is None:
            return {"accepted": False, "reason": "disabled/phase_not_started"}
        step = self._step(global_step)
        if step <= self.last_validation_step or self.validation_step not in (None, step):
            raise ValueError("validation batches share one increasing checkpoint step")
        value, weight = self._number(loss), self._number(loss_weight)
        if weight <= 0:
            raise ValueError("positive validation weight required")
        self.validation_step = step
        self.validation[0] += value * weight
        self.validation[1] += weight
        return {"accepted": True}

    def end_phase(self, **kwargs):
        if self.validation is None or not self.is_enabled():
            return
        total, weight = self.validation
        self.validation = None
        if weight:
            self.writer.add_scalar(self._tag("validation", "loss"), total / weight, self.validation_step)
            self.last_validation_step = self.validation_step

    def flush(self):
        if self.is_enabled():
            self.writer.flush()

    def status(self):
        return {"backend": "tensorboard", "closed": self.closed,
                "scope": "rank_0" if self.world_size > 1 else "single_rank",
                "unsupported": ["gradient", "latency", "memory", "global_aggregation", "live_reload"]}

    def close(self):
        if not self.closed:
            try:
                self.end_phase()
            finally:
                if self.writer is not None:
                    try:
                        self.writer.flush()
                    finally:
                        self.writer.close()
            self.closed = True
        return {"closed": self.closed, "error": None, "pending_records": 0}


class OptionalTrainingMonitor:
    """Select a backend once, preserving the existing training and handoff APIs."""

    _methods = {"is_enabled", "start_phase", "end_phase", "record_train", "record_validation",
                "capture_gradients", "reenable", "configure", "poll_config", "flush",
                "state_dict", "load_state_dict"}

    def __init__(self, factory, *, output_dir, run_id, attempt_id, rank=0, world_size=1,
                 record_every_updates=10, flush_secs=10):
        self.monitor, self.backend, self.reason = None, "disabled", None
        self._warnings = set()
        self.output_dir = None
        self.run_id, self.attempt_id, self.rank = run_id, attempt_id, rank
        if os.environ.get("ONECODE_MONITORING_DISABLED") == "1":
            self._warn("monitoring_explicitly_disabled")
            return
        try:
            self.output_dir = Path(output_dir)
            if (not self.output_dir.is_absolute() or not isinstance(run_id, str) or not run_id
                    or not isinstance(attempt_id, str) or not attempt_id
                    or not isinstance(rank, int) or not isinstance(world_size, int) or not 0 <= rank < world_size):
                raise ValueError("absolute output directory and valid runtime identity/rank required")
        except Exception as error:
            self._warn("invalid_monitoring_context", error)
            return
        primary = None
        try:
            primary = factory()
            config = getattr(primary, "config", None)
            if config is None or getattr(primary, "initialization_error", None):
                raise ValueError("OneScience monitor unavailable")
            if (config.run_id != run_id or config.attempt_id != attempt_id or
                    Path(config.output_dir).resolve() != self.output_dir.resolve()):
                raise ValueError("OneScience monitor context mismatch")
            self.monitor, self.backend = primary, "onescience"
        except Exception as error:
            if primary is not None:
                try:
                    primary.close()
                except Exception:
                    pass
            self._warn("onescience_unavailable", error)
        if self.monitor is None:
            try:
                self.monitor = TensorBoardMonitor(self.output_dir, rank=rank, world_size=world_size,
                    record_every_updates=record_every_updates, flush_secs=flush_secs)
                self.backend = "tensorboard"
            except Exception as error:
                self._warn("tensorboard_unavailable", error)

    def _warn(self, code, error=None):
        self.reason = code
        if code in self._warnings:
            return
        self._warnings.add(code)
        try:
            print("ONECODE_MONITORING_WARNING " + json.dumps({"code": code,
                "error_type": type(error).__name__ if error else None, "backend": self.backend,
                "training_continues": True}), file=sys.stderr, flush=True)
        except Exception:
            pass

    def _call(self, name, *args, **kwargs):
        if self.monitor is None:
            return False if name == "is_enabled" else None
        method = getattr(self.monitor, name, None)
        if method is None:
            return {"accepted": False, "reason": "unsupported"}
        try:
            result = method(*args, **kwargs)
            if isinstance(result, dict) and result.get("reason") == "non_increasing_step":
                self._warn("monitoring_non_increasing_step")
            return result
        except Exception as error:
            self._warn("monitoring_operation_failed", error)
            return False if name == "is_enabled" else None

    def __getattr__(self, name):
        if name not in self._methods:
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
        try:
            yield
        finally:
            if entered:
                try:
                    stage.__exit__(None, None, None)
                except Exception as error:
                    self._warn("monitoring_stage_close_failed", error)

    def status(self):
        return {"backend": self.backend, "reason": self.reason, "output_dir": str(self.output_dir),
                "warnings": sorted(self._warnings), "component": self._call("status")}

    def publish_runtime(self, event_root, title):
        """Existing optional OneCode handoff; no new collection protocol."""
        if self.monitor is None or self.rank != 0:
            return False
        required = ["ONECODE_TASK_ID", "ONECODE_RUN_ID", "ONECODE_ATTEMPT_ID",
                    "ONECODE_EXECUTION_TARGET", "ONECODE_RUNTIME_MANIFEST"]
        if not all(os.environ.get(key, "").strip() for key in required):
            self._warn("platform_identity_unavailable")
            return False
        temporary = None
        try:
            if self.run_id != os.environ["ONECODE_RUN_ID"] or self.attempt_id != os.environ["ONECODE_ATTEMPT_ID"]:
                raise ValueError("monitor identity differs from platform identity")
            target = Path(os.environ["ONECODE_RUNTIME_MANIFEST"])
            if not target.is_absolute() or not Path(event_root).is_absolute():
                raise ValueError("absolute runtime/event paths required")
            event = {"schema": "onecode.training/v1", "kind": "training", "title": title,
                     "taskId": os.environ["ONECODE_TASK_ID"], "runId": self.run_id,
                     "attemptId": self.attempt_id, "executionTargetRef": os.environ["ONECODE_EXECUTION_TARGET"],
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
