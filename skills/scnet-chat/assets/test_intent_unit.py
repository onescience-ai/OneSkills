# -*- coding: utf-8 -*-
"""
意图识别单元测试（不访问网络）。
运行: python -m pytest assets/test_intent_unit.py -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from scnet import IntentRecognizer  # noqa: E402


def _fake_clusters():
    return {
        "昆山": "华东一区【昆山】",
        "山东": "山东中心",
        "西安": "西安",
    }


@patch.object(IntentRecognizer, "_load_clusters", return_value=_fake_clusters())
class TestIntentRecognizer(unittest.TestCase):
    def test_cache_refresh(self, _mock):
        intent, _ = IntentRecognizer().recognize("刷新缓存")
        self.assertEqual(intent, "cache_refresh")

    def test_switch_cluster(self, _mock):
        intent, p = IntentRecognizer().recognize("切换到山东")
        self.assertEqual(intent, "switch_cluster")
        self.assertEqual(p.get("cluster_name"), "山东中心")

    def test_user_info(self, _mock):
        intent, _ = IntentRecognizer().recognize("查询用户")
        self.assertEqual(intent, "user_info")

    def test_user_info_excludes_job_query(self, _mock):
        intent, p = IntentRecognizer().recognize("查询用户 zhangsan 的作业")
        self.assertNotEqual(intent, "user_info")
        self.assertEqual(p.get("cluster_user_name"), "zhangsan")

    def test_job_list(self, _mock):
        intent, _ = IntentRecognizer().recognize("查询作业")
        self.assertEqual(intent, "job_list")

    def test_job_history_days_chinese(self, _mock):
        intent, p = IntentRecognizer().recognize("查询最近三天的历史作业")
        self.assertEqual(intent, "job_history")
        self.assertEqual(p.get("days"), 3)

    def test_job_history_date_range(self, _mock):
        intent, p = IntentRecognizer().recognize("查询从2026-04-01到2026-04-03的历史作业")
        self.assertEqual(intent, "job_history")
        self.assertIn("2026-04-01", p.get("start_time", ""))
        self.assertIn("2026-04-03", p.get("end_time", ""))

    def test_job_submit_simple_cmd(self, _mock):
        intent, p = IntentRecognizer().recognize("提交作业 sleep 10")
        self.assertEqual(intent, "job_submit")
        self.assertEqual(p.get("cmd"), "sleep 10")

    def test_job_submit_queue_chinese_colon(self, _mock):
        intent, p = IntentRecognizer().recognize("提交作业 sleep 5 队列：debug")
        self.assertEqual(intent, "job_submit")
        self.assertEqual(p.get("cmd"), "sleep 5")
        self.assertEqual(p.get("queue"), "debug")

    def test_job_submit_in_region(self, _mock):
        intent, p = IntentRecognizer().recognize("在昆山提交作业 sleep 1")
        self.assertEqual(intent, "job_submit")
        self.assertEqual(p.get("cluster_name"), "华东一区【昆山】")
        self.assertEqual(p.get("cmd"), "sleep 1")

    def test_job_submit_help(self, _mock):
        intent, _ = IntentRecognizer().recognize("提交作业帮助")
        self.assertEqual(intent, "job_submit_help")

    def test_file_list_before_cluster_switch(self, _mock):
        """含路径时不应误判为区域切换。"""
        intent, p = IntentRecognizer().recognize("查看文件 /public/home/user/scnet")
        self.assertEqual(intent, "file_list")
        self.assertIn("/public/home/user/scnet", p.get("path") or "")

    def test_job_filter_status(self, _mock):
        intent, p = IntentRecognizer().recognize("查询历史作业，状态为失败")
        self.assertEqual(intent, "job_history")
        self.assertEqual(p.get("status"), "statD")

    def test_job_filter_page_chinese(self, _mock):
        intent, p = IntentRecognizer().recognize("查询历史作业，每页5条，显示第二页")
        self.assertEqual(intent, "job_history")
        self.assertEqual(p.get("page"), 2)
        self.assertEqual(p.get("size"), 5)


if __name__ == "__main__":
    unittest.main()
