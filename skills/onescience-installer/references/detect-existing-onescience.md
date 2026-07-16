# 工作流 - 检测已有 OneScience

当 `onescience.json.runtime.conda` 缺失时读取本工作流。

## 目的

判断目标环境是否已经存在 `onescience` 和 `torch` 包。如果已经存在，记录环境信息；如果不存在，检测指定的 conda 环境。**本工作流只检测，不创建环境，不安装包。**

## 步骤

1. 获取目标 conda 环境名：
   - 优先使用用户指定的环境名（如用户说"检测 xx 环境"）
   - 否则从 `backend_profiles.json.defaults.env_name` 获取默认值（通常是 `onescience311`）
   
2. 创建并执行简化检测命令：
   - `run_site=remote`：使用 `install_flow.md` 的 `§0d` 模板，通过临时 Python 脚本检测。
   - `run_site=local`：使用 `install_flow.md` 的 `§0e` 模板，通过本地 Python 脚本检测。
   
3. 检测内容包括：
   - Python 版本
   - 当前环境是否有 `onescience` 和 `torch` 包及其版本
   - 是否有 `conda` 命令
   - 指定的 conda 环境（{env_name}）是否存在
   - 若该 conda 环境存在，检测其中是否有 `onescience` 和 `torch` 包及其版本

4. 根据检测结果处理：

   **情况 A：当前环境有 onescience 和 torch**
   - 读取 `writeback-conda-state.md`
   - 写回 `onescience.json.runtime.conda`：
     ```json
     {
       "runtime": {
         "conda": {
           "enabled": false
         }
       }
     }
     ```
   - 输出 `install_state=current_env_ready`
   - 返回上游调用方或 `onescience-orchestrator`

   **情况 B：当前环境没有，但指定的 conda 环境有 onescience 和 torch**
   - 读取 `writeback-conda-state.md`
   - 写回 `onescience.json.runtime.conda`：
     ```json
     {
       "runtime": {
         "conda": {
           "enabled": true,
           "env_name": "{env_name}",
           "activate_script": "conda activate {env_name}"
         }
       }
     }
     ```
   - 输出 `install_state=conda_env_ready`
   - 返回上游调用方或 `onescience-orchestrator`

   **情况 C：当前环境和指定 conda 环境都没有 onescience**
   - 输出检测报告：
     ```
     环境检测结果：
     - 当前环境：Python <版本或未找到>，onescience: 未安装，torch: <状态>
     - Conda: <found/not_found>
     - Conda 环境 {env_name}: <exists/not_found>
     
     没有找到可用的 OneScience 环境。
     ```
   - 询问用户：**是否创建 conda 环境安装 onescience 和其它用户明确需要的包？**
   - 如果用户确认创建：
     - 向用户确认要创建的 conda 环境名称，默认为从 `backend_profiles.json.defaults.env_name` 获取的值（通常是 `onescience311`）
     - 用户可以确认使用默认名称，或提供其它名称
     - 然后路由到 `install-onescience-conda.md` 创建 conda 环境并安装 onescience 包
   - 如果用户不安装：
     - **不写入或更新** `onescience.json.runtime.conda`
     - 输出 `install_state=no_environment_user_declined`
     - 返回上游调用方或 `onescience-orchestrator`

5. 本工作流**不得执行安装命令**，不得创建 conda 环境，不得询问用户是否要安装。
