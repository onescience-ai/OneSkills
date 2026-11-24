# OneCode 代码生成与执行交接

代码阶段读取 tasks/revision，通过 save_task 合并稳定任务，保存真实 entrypoint、业务 config、实际 execution_entrypoints 和 monitoring.requested=true；不保存运行身份或凭据。先生成后执行、同轮生成执行均走原入口，继承“暂不运行”。

## 运行时绑定配置

平台只注入 ONECODE_* 身份和清单上下文，不保证替你生成 ONESC_MONITOR_CONFIG。业务训练脚本在启动后、进入可选监控初始化边界内读取注入 run/attempt，构建独立绝对 output_dir（例如项目配置允许的 monitor 根目录/run/attempt），再创建 MonitorConfig；或写本次独立配置文件后 from_file。ONESC_MONITOR_CONFIG 若使用，必须指向这份本次实际配置，禁止所有任务共享覆盖同一个文件。

未拿到完整身份时可以独立采集，但不能伪造平台身份、默认写共享 runtime.json 或称已关联。sbatch 脚本保留环境导出，不用 --export=NONE 丢弃身份；Slurm spool 中的 BASH_SOURCE 不能用来推断项目路径，使用已配置的实际工作目录。

## 初始化后报告运行清单

以下是知识片段，不是独立启动器。与通用工具卡 open/close 边界配合使用；rank 用业务实际全局 rank。该函数不负责指标写入，也不属于 OneScience 公共接口。

```python
def onecode_runtime_context(output_root):
    import os
    from pathlib import Path
    keys = ("ONECODE_TASK_ID", "ONECODE_RUN_ID", "ONECODE_ATTEMPT_ID",
            "ONECODE_EXECUTION_TARGET", "ONECODE_RUNTIME_MANIFEST")
    if not all(os.environ.get(key, "").strip() for key in keys):
        return None  # Independent execution must not forge a platform association.
    root = Path(output_root).resolve() / os.environ["ONECODE_RUN_ID"] / os.environ["ONECODE_ATTEMPT_ID"]
    return {"schema":"onecode.training/v1", "kind":"training", "taskId":os.environ["ONECODE_TASK_ID"],
            "runId":os.environ["ONECODE_RUN_ID"], "attemptId":os.environ["ONECODE_ATTEMPT_ID"],
            "executionTargetRef":os.environ["ONECODE_EXECUTION_TARGET"], "eventRoot":str(root)}

def publish_onecode_runtime(context, *, title, rank, training_exit_code=None):
    import json
    import logging
    import os
    import tempfile
    from pathlib import Path
    if rank != 0 or context is None:
        return False
    temporary = None
    try:
        for field, key in (("taskId","ONECODE_TASK_ID"),("runId","ONECODE_RUN_ID"),
                           ("attemptId","ONECODE_ATTEMPT_ID"),("executionTargetRef","ONECODE_EXECUTION_TARGET")):
            if context[field] != os.environ[key]:
                raise ValueError("platform identity mismatch")
        target=Path(os.environ["ONECODE_RUNTIME_MANIFEST"])
        if not target.is_absolute() or not Path(context["eventRoot"]).is_absolute():
            raise ValueError("absolute runtime/event paths required")
        event=dict(context,title=title)
        if os.environ.get("ONECODE_REGION"):
            event["region"]=os.environ["ONECODE_REGION"]
        if os.environ.get("SLURM_JOB_ID"):
            event.update(jobRef=os.environ["SLURM_JOB_ID"],scheduler="slurm")
        if training_exit_code is not None:
            if isinstance(training_exit_code,bool) or not isinstance(training_exit_code,int) or not 0<=training_exit_code<=255:
                raise ValueError("invalid training exit code")
            event["trainingExitCode"]=training_exit_code
        target.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",dir=target.parent,delete=False) as stream:
            temporary=stream.name
            json.dump(event,stream)
        os.replace(temporary,target)
        return True
    except Exception as error:
        logging.getLogger("training.monitoring").warning("runtime report unavailable (%s); training continues",type(error).__name__)
        return False
    finally:
        if temporary:
            try: Path(temporary).unlink(missing_ok=True)
            except OSError: pass
```

先 `context=onecode_runtime_context(项目监控根目录)`，再在监控专属初始化边界中用 MonitorConfig(output_dir=context["eventRoot"],run_id=context["runId"],attempt_id=context["attemptId"],profile="base",record_every_updates=1,shutdown_timeout_seconds=120) 创建当前配置；其它选项依据通用卡和实际版本选择。不要只等 ONESC_MONITOR_CONFIG：平台注入的是 ONECODE_*，不会自动生成该变量指向的文件。

初始化后 `publish_onecode_runtime(context,title=实际标题,rank=rank)`，训练体用 try/except/finally 保留原异常；正常训练结束设置 training_exit_code=0，真实训练异常设置非零并重新抛出。finally 中先用通用窄边界关闭监控，再用 `publish_onecode_runtime(context,title=实际标题,rank=rank,training_exit_code=实际训练退出码)` 报告结束；即使监控初始化失败，context 仍可上报真实训练结果。监控 verify/writer/关闭失败不能把该训练退出码改成失败。MONITOR_EVENT_DIR 文本不是替代上报。

当 context 存在时不能自行生成 run/attempt；当 context 不存在时才按明确的独立运行配置执行，不伪造平台绑定。可选 region/jobRef 没有值时省略，不填空字符串。写入失败只记录监控警告。

## 查看和诊断顺序

先只读查询当前记录，区分训练结果、来源绑定、三阶段状态、缓存和查看错误。已有曲线走缓存查看；仅需查看时不先探测远端、不安装依赖、不生成新作业。修复来源需授权并走平台入口及 revision 校验，不能通过重训或手改数据库解决展示错误。
