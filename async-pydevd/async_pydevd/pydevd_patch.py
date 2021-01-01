def is_async_code(code: str) -> bool:
    return "__async_eval__" not in code and ("await" in code or "async" in code)


def make_code_async(code: str) -> str:
    if not code:
        return code

    if is_async_code(code):
        code = code.replace("@" + "LINE" + "@", "\n")
        return f"__import__('sys').__async_eval__({code!r}, globals(), locals())"

    return code


# 1. Add ability to evaluate async expression
from _pydevd_bundle import pydevd_vars

original_evaluate = pydevd_vars.evaluate_expression


def evaluate_expression(thread_id: int, frame_id: int, expression: str, doExec: bool):
    if is_async_code(expression):
        doExec = False

    return original_evaluate(thread_id, frame_id, make_code_async(expression), doExec)


pydevd_vars.evaluate_expression = evaluate_expression

# 2. Add ability to use async breakpoint conditions
from _pydevd_bundle.pydevd_breakpoints import LineBreakpoint


def normalize_line_breakpoint(line_breakpoint: LineBreakpoint) -> None:
    line_breakpoint.expression = make_code_async(line_breakpoint.expression)
    line_breakpoint.condition = make_code_async(line_breakpoint.condition)


original_init = LineBreakpoint.__init__


def line_breakpoint_init(self: LineBreakpoint, *args, **kwargs):
    original_init(self, *args, **kwargs)
    normalize_line_breakpoint(self)


LineBreakpoint.__init__ = line_breakpoint_init

# 3. Add ability to use async code in console
from _pydevd_bundle import pydevd_console_integration

original_console_exec = pydevd_console_integration.console_exec


def console_exec(thread_id: int, frame_id: int, expression: str, dbg):
    return original_console_exec(thread_id, frame_id, make_code_async(expression), dbg)


pydevd_console_integration.console_exec = console_exec

# 4. Add ability to use async code
from _pydev_bundle.pydev_console_types import Command


def command_run(self):
    text = make_code_async(self.code_fragment.text)
    symbol = self.symbol_for_fragment(self.code_fragment)

    self.more = self.interpreter.runsource(text, "<input>", symbol)


Command.run = command_run
