import importlib.util
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('adapter', Path(__file__).with_name('training_monitor_adapter.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
OptionalTrainingMonitor = module.OptionalTrainingMonitor


class FakeMonitor:
    config = SimpleNamespace(run_id='run', attempt_id='attempt')
    initialization_error = None

    def record_train(self, **kwargs):
        raise OSError('write failed')

    def close(self):
        raise TimeoutError('close failed')


class AdapterTests(unittest.TestCase):
    def test_missing_optional_dependency_does_not_prevent_training(self):
        def factory():
            raise ModuleNotFoundError('onescience')
        with OptionalTrainingMonitor(factory) as monitor:
            monitor.start_phase('train')
            training_updates = sum(range(4))
            monitor.record_train(global_step=1, micro_step=1, loss=1.0)
        self.assertEqual(training_updates, 6)
        self.assertEqual(monitor.reason, 'monitoring_initialization_failed')

    def test_monitor_failures_do_not_mask_real_training_failure(self):
        monitor = OptionalTrainingMonitor(FakeMonitor)
        with self.assertRaisesRegex(ValueError, 'actual backprop failure'):
            with monitor:
                with monitor.stage('backward'):
                    monitor.record_train(loss=1.0)
                    raise ValueError('actual backprop failure')
        self.assertIn('monitoring_operation_failed', monitor._warnings)

    def test_report_requires_complete_and_matching_platform_identity(self):
        with tempfile.TemporaryDirectory() as root:
            target = Path(root)/'attempt/runtime.json'
            env = {'ONECODE_RUNTIME_MANIFEST': str(target), 'ONECODE_TASK_ID': 'task',
                   'ONECODE_RUN_ID': 'run', 'ONECODE_ATTEMPT_ID': 'attempt',
                   'ONECODE_EXECUTION_TARGET': 'saved-ssh', 'SLURM_JOB_ID': '900', 'RANK': '0'}
            with patch.dict(os.environ, env, clear=True):
                monitor = OptionalTrainingMonitor(FakeMonitor)
                self.assertTrue(monitor.publish_runtime(str(Path(root)/'events'), 'Model'))
                report = json.loads(target.read_text())
                self.assertEqual(report['attemptId'], 'attempt')
                self.assertEqual(report['jobRef'], '900')
                target.unlink()
                os.environ['ONECODE_TASK_ID'] = ''
                self.assertFalse(monitor.publish_runtime(root, 'Model'))
                self.assertFalse(target.exists())
                os.environ['ONECODE_TASK_ID'] = 'task'
                os.environ['ONECODE_ATTEMPT_ID'] = 'foreign'
                self.assertFalse(monitor.publish_runtime(root, 'Model'))
                self.assertFalse(target.exists())

    def test_publication_failure_does_not_change_training(self):
        with tempfile.TemporaryDirectory() as root:
            target = Path(root)/'not-a-directory'
            target.write_text('file')
            with patch.dict(os.environ, {'ONECODE_RUNTIME_MANIFEST': str(target/'runtime.json'),
                    'ONECODE_TASK_ID': 'task', 'ONECODE_RUN_ID': 'run', 'ONECODE_ATTEMPT_ID': 'attempt',
                    'ONECODE_EXECUTION_TARGET': 'saved-ssh'}, clear=True):
                monitor = OptionalTrainingMonitor(FakeMonitor)
                self.assertFalse(monitor.publish_runtime(root, 'Model'))
                self.assertEqual(monitor.reason, 'monitoring_runtime_publication_failed')

    @unittest.skipUnless(os.environ.get('ONECODE_TEST_ONESCIENCE_SOURCE'), 'requires actual OneScience source')
    def test_actual_onescience_writer_closes_and_validates(self):
        from onescience.monitoring.training import MonitorConfig, create_monitor, verify
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)/'attempt'
            with patch.dict(os.environ, {'ONECODE_MONITORING_DISABLED': '0'}):
                monitor = OptionalTrainingMonitor(lambda: create_monitor(MonitorConfig(str(root), 'run', 'attempt',
                    record_every_updates=1, train_mode='writer_local', validation_mode='writer_local'), rank=0, world_size=1))
                self.assertIsNotNone(monitor.monitor)
                monitor.start_phase('train')
                for step in (1, 2, 3):
                    monitor.record_train(global_step=step, micro_step=step, loss=1.0/step, loss_weight=1)
                monitor.end_phase()
                result = monitor.close()
                self.assertTrue(result['closed'])
                self.assertFalse(result['error'])
                self.assertEqual(verify(root)['status'], 'ok')


if __name__ == '__main__':
    unittest.main()
