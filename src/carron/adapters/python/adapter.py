"""Python runtime adapter implementing v0.1 target semantics."""

import ast
import importlib
import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from carron.interfaces.adapter import (
    Adapter,
    InvalidSourceError,
    TargetParseError,
    TargetRef,
    TargetResolutionError,
)

SourceKind = Literal["module", "file"]
ObjectKind = Literal["function", "method", "unknown"]


@dataclass(frozen=True)
class _PythonTarget:
    """Internal representation of a parsed Python target."""

    raw: str
    source_kind: SourceKind
    locator: str
    qualname: str
    class_name: str | None
    attr_name: str


@dataclass(frozen=True)
class PythonTargetSummary:
    """Best-effort summary of a Python target."""

    found: bool
    importable: bool
    object_kind: ObjectKind
    signature: str | None
    doc: str | None
    diagnostics: list[str]


@dataclass(frozen=True)
class PythonValidatedTarget:
    """Validated Python target payload passed to forges."""

    target: _PythonTarget
    payload: Any


class PythonRuntimeAdapter(Adapter):
    """Python adapter implementing v0.1 runtime behavior.

    Supported target forms:

    - module:func
    - module:Class.method
    - file.py:func
    - file.py:Class.method

    File targets are resolved via read + AST.
    Module targets are resolved via import + inspect.
    """

    def get_target_summary(self, ref: TargetRef) -> PythonTargetSummary:
        """Return a best-effort summary of a Python target."""
        target = self._parse(ref.raw)

        if target.source_kind == "file":
            tree = self._parse_file_ast(target.locator)
            node = self._find_node(tree, target)
            return PythonTargetSummary(
                found=True,
                importable=False,
                object_kind=self._node_kind(target),
                signature=self._ast_signature(node),
                doc=self._first_doc_line(ast.get_docstring(node)),
                diagnostics=[],
            )

        diagnostics: list[str] = []

        try:
            module = importlib.import_module(target.locator)
        except Exception as exc:  # Best-effort by design
            diagnostics.append(f"Import failed: {exc.__class__.__name__}: {exc}")
            return PythonTargetSummary(
                found=False,
                importable=False,
                object_kind="unknown",
                signature=None,
                doc=None,
                diagnostics=diagnostics,
            )

        try:
            obj = self._resolve_from_module(module, target)
        except Exception as exc:
            diagnostics.append(f"Symbol not found: {exc}")
            return PythonTargetSummary(
                found=False,
                importable=True,
                object_kind="unknown",
                signature=None,
                doc=None,
                diagnostics=diagnostics,
            )

        return PythonTargetSummary(
            found=True,
            importable=True,
            object_kind=self._object_kind(obj, target),
            signature=self._safe_signature(obj),
            doc=self._first_doc_line(inspect.getdoc(obj)),
            diagnostics=diagnostics,
        )

    def validate_target(self, ref: TargetRef) -> PythonValidatedTarget:
        """Strictly validate and resolve a Python target."""
        target = self._parse(ref.raw)

        if target.source_kind == "file":
            tree = self._parse_file_ast(target.locator)
            node = self._find_node(tree, target)
            return PythonValidatedTarget(target=target, payload={"ast": tree, "node": node})

        try:
            module = importlib.import_module(target.locator)
        except Exception as exc:
            raise TargetResolutionError(
                f"Failed to import module '{target.locator}': {exc}"
            ) from exc

        try:
            obj = self._resolve_from_module(module, target)
        except Exception as exc:
            raise TargetResolutionError(
                f"Symbol '{target.qualname}' not found in module '{target.locator}'"
            ) from exc

        return PythonValidatedTarget(target=target, payload={"object": obj})

    def _parse(self, raw: str) -> _PythonTarget:
        """Parse a raw Python target string."""
        if ":" not in raw:
            raise TargetParseError("Target must be in form 'module:qualname' or 'file.py:qualname'")

        locator, qualname = raw.split(":", 1)
        locator = locator.strip()
        qualname = qualname.strip()

        if not locator or not qualname:
            raise TargetParseError("Target must have non-empty locator and qualname")

        if "." in qualname:
            parts = qualname.split(".")
            if len(parts) != 2 or not parts[0] or not parts[1]:
                raise TargetParseError("Only 'Class.method' qualnames are supported")
            class_name, attr_name = parts
        else:
            class_name = None
            attr_name = qualname

        source_kind: SourceKind = "file" if locator.endswith(".py") else "module"

        return _PythonTarget(
            raw=raw,
            source_kind=source_kind,
            locator=locator,
            qualname=qualname,
            class_name=class_name,
            attr_name=attr_name,
        )

    def _parse_file_ast(self, path: str) -> ast.Module:
        """Read and parse a Python file into an AST."""
        try:
            source = Path(path).read_text()
        except FileNotFoundError as exc:
            raise TargetResolutionError(f"File not found: {path}") from exc

        try:
            return ast.parse(source, filename=path)
        except SyntaxError as exc:
            raise InvalidSourceError(
                f"Invalid Python in {path}: {exc.msg} (line {exc.lineno})"
            ) from exc

    def _find_node(
        self, tree: ast.Module, target: _PythonTarget
    ) -> ast.FunctionDef | ast.AsyncFunctionDef:
        """Locate the requested function or method in the AST."""
        for node in tree.body:
            if target.class_name is None:
                if (
                    isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
                    and node.name == target.attr_name
                ):
                    return node
                continue

            if isinstance(node, ast.ClassDef) and node.name == target.class_name:
                for child in node.body:
                    if (
                        isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef)
                        and child.name == target.attr_name
                    ):
                        return child
                raise TargetResolutionError(
                    f"Method '{target.class_name}.{target.attr_name}' not found"
                )

        if target.class_name is None:
            raise TargetResolutionError(f"Function '{target.attr_name}' not found")

        raise TargetResolutionError(f"Class '{target.class_name}' not found")

    def _resolve_from_module(self, module: Any, target: _PythonTarget) -> Any:
        """Resolve a target from an imported module."""
        if target.class_name is None:
            return getattr(module, target.attr_name)

        cls = getattr(module, target.class_name)
        return getattr(cls, target.attr_name)

    def _safe_signature(self, obj: Any) -> str | None:
        """Safely obtain a string representation of an object's signature."""
        try:
            return str(inspect.signature(obj))
        except Exception:
            return None

    def _node_kind(self, target: _PythonTarget) -> ObjectKind:
        """Return the object kind for a file-based target."""
        return "method" if target.class_name else "function"

    def _object_kind(self, obj: Any, target: _PythonTarget) -> ObjectKind:
        """Return the object kind for a module-based target."""
        if target.class_name:
            return "method"
        if inspect.isfunction(obj):
            return "function"
        return "unknown"

    def _ast_signature(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> str | None:
        """Return a best-effort string signature from an AST node."""
        args = node.args
        parts: list[str] = []

        for arg in getattr(args, "args", []):
            parts.append(arg.arg)

        if args.vararg:
            parts.append(f"*{args.vararg.arg}")

        for arg in getattr(args, "kwonlyargs", []):
            parts.append(arg.arg)

        if args.kwarg:
            parts.append(f"**{args.kwarg.arg}")

        return f"({', '.join(parts)})"

    def _first_doc_line(self, doc: str | None) -> str | None:
        """Return the first line of a docstring, if present."""
        if not doc:
            return None
        return doc.splitlines()[0].strip() or None
