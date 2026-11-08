"""エージェントの配線テスト。

TestModel は実際のLLMを呼ばない偽モデルで、登録されたツールを全部呼んでから
ダミーの回答を返す。APIキーも利用枠も使わずに、
「ツールが登録され、呼ばれ、結果がモデルに戻るか」を確かめられる。
"""

from pydantic_ai import DeferredToolRequests
from pydantic_ai.messages import ToolCallPart, ToolReturnPart
from pydantic_ai.models.test import TestModel

from app.agent import agent, main, prompt_for_deferred_approvals

BASE_TOOLS = {"search_glossary", "get_lecture_summary"}


def _parts(result, kind):
    return [p for m in result.all_messages() for p in m.parts if isinstance(p, kind)]


def test_base_tools_are_registered_and_called():
    model = TestModel(call_tools=["search_glossary", "get_lecture_summary"])
    with agent.override(model=model):
        result = agent.run_sync("LoRAとは？")

    offered = {t.name for t in model.last_model_request_parameters.function_tools}
    assert BASE_TOOLS <= offered  # 演習でツールを足しても壊れないよう「含む」で判定

    called = {p.tool_name for p in _parts(result, ToolCallPart)}
    assert BASE_TOOLS <= called
    # 承認が必要なツール（requires_approval=True）は、実行されずに承認待ちになるので戻り値が無い
    waiting = len(result.output.approvals) if isinstance(result.output, DeferredToolRequests) else 0
    assert len(_parts(result, ToolReturnPart)) + waiting == len(_parts(result, ToolCallPart))
    assert result.output


def test_glossary_result_reaches_the_model():
    model = TestModel(call_tools=["search_glossary"])
    with agent.override(model=model):
        result = agent.run_sync("RAGとは？")
    returns = _parts(result, ToolReturnPart)
    assert returns and returns[0].tool_name == "search_glossary"


def test_learning_log_tool_waits_for_approval(tmp_path, monkeypatch):
    from app import tools

    log_path = tmp_path / "entries.jsonl"
    monkeypatch.setattr(tools, "LEARNING_LOG_PATH", log_path)

    with agent.override(model=TestModel(call_tools=["save_learning_log"])):
        pending = agent.run_sync("学習内容を保存して")

    assert isinstance(pending.output, DeferredToolRequests)
    call = pending.output.approvals[0]
    assert call.tool_name == "save_learning_log"
    assert not log_path.exists()

    deferred_results = pending.output.build_results(
        approvals={call.tool_call_id: True}
    )
    with agent.override(model=TestModel(call_tools=[])):
        completed = agent.run_sync(
            message_history=pending.all_messages(),
            deferred_tool_results=deferred_results,
        )

    assert isinstance(completed.output, str)
    assert log_path.read_text(encoding="utf-8") == '{"content": "a"}\n'


def test_learning_log_rejection_does_not_write(tmp_path, monkeypatch, capsys):
    from app import tools

    log_path = tmp_path / "entries.jsonl"
    monkeypatch.setattr(tools, "LEARNING_LOG_PATH", log_path)
    with agent.override(model=TestModel(call_tools=["save_learning_log"])):
        pending = agent.run_sync("学習内容を保存して")
    assert isinstance(pending.output, DeferredToolRequests)
    call = pending.output.approvals[0]

    for answer in ("n", ""):
        monkeypatch.setattr("builtins.input", lambda _prompt, answer=answer: answer)
        deferred_results = prompt_for_deferred_approvals(pending.output)
        assert deferred_results.approvals == {call.tool_call_id: False}
        output = capsys.readouterr().out
        assert str(log_path) in output
        assert "保存予定の内容:" in output
        with agent.override(model=TestModel(call_tools=[])):
            completed = agent.run_sync(
                message_history=pending.all_messages(),
                deferred_tool_results=deferred_results,
            )
        assert isinstance(completed.output, str)
        assert not log_path.exists()


def test_trace_cli_works_with_test_model(monkeypatch, capsys):
    monkeypatch.setattr(
        "app.agent.build_model",
        lambda: TestModel(call_tools=["search_glossary"]),
    )
    monkeypatch.setattr("sys.argv", ["app.agent", "--trace", "LoRAとは？"])

    main()

    assert "[tool call]   search_glossary" in capsys.readouterr().out
