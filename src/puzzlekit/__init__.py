from typing import Dict, Any, Optional, Union
from puzzlekit.solvers import get_solver_class
from puzzlekit.parsers.registry import get_parser 
from puzzlekit.formats.base import PuzzleInstance
from puzzlekit.formats.puzzlink_converter import PuzzlinkConverter
from puzzlekit.formats.penpa_converter import (
    PenpaConverter,
    PENPA_PREFIX,
    PENPA_URLPREFIX,
)


_FORMAT_ALIASES = {
    "puzzlink": "puzzlink",
    "pzl": "puzzlink",
    "penpa": "penpa",
    "ppa": "penpa",
    "ir": "ir",
    "instance": "ir",
    "puzzleinstance": "ir",
}


def _normalize_format_name(name: str) -> str:
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Format name must be a non-empty string.")
    key = name.strip().lower()
    if key not in _FORMAT_ALIASES:
        raise ValueError(f"Unknown format '{name}'. Supported: puzzlink, penpa, ir.")
    return _FORMAT_ALIASES[key]


def _normalize_penpa_source(source: str) -> str:
    s = source.strip()
    if s.startswith("#"):
        s = s[1:]
    if s.startswith(PENPA_PREFIX):
        return s
    if s.startswith(PENPA_URLPREFIX):
        frag = s.split("#", 1)[1] if "#" in s else ""
        if frag.startswith("#"):
            frag = frag[1:]
        return frag if frag.startswith(PENPA_PREFIX) else f"{PENPA_PREFIX}{frag}"
    return s


def _detect_source_format(source: str) -> str:
    s = source.strip()
    if "puzz.link/p?" in s:
        return "puzzlink"
    if s.startswith(PENPA_PREFIX) or s.startswith("#" + PENPA_PREFIX) or PENPA_URLPREFIX in s:
        return "penpa"
    raise ValueError("Cannot detect source format. Please pass source_format explicitly.")


def _build_converter(fmt: str, converter_config: Optional[Dict[str, Any]] = None):
    if fmt == "puzzlink":
        return PuzzlinkConverter(converter_config or {})
    if fmt == "penpa":
        return PenpaConverter(converter_config or {})
    raise ValueError(f"Unsupported converter format '{fmt}'.")

def solve(
    source: Union[str, Dict[str, Any]], 
    puzzle_type: str, 
    **kwargs
) -> Any:
    """
    Unified entry point for solving puzzles.
    
    Args:
        source: 
            - A string containing the raw puzzle data (with headers, e.g. "9 9\n...").
            - A dictionary (pre-parsed data).
        puzzle_type: The snake_case type name (e.g., 'akari', 'fuzuli').
        show: Whether to visualize the result.
        **kwargs: Overrides for solver parameters.
    """
    
    # --- 1.  (Parsing) ---
    init_params = {}
    
    if isinstance(source, dict):
        init_params = source.copy()
        
    elif isinstance(source, str):
        try:
            target_parser = get_parser(puzzle_type) 
            parsed_data = target_parser(source.strip())
            
            if parsed_data is None:
                raise ValueError(f"Parser returned None for type '{puzzle_type}'")
                
            init_params.update(parsed_data)
        except ValueError as e:
            raise ValueError(f"Parsing failed for type '{puzzle_type}': {e}")
            
    else:
        raise TypeError(f"Source must be dict or raw string, got {type(source)}")
    
    init_params.update(kwargs)

    try:
        SolverClass = get_solver_class(puzzle_type)
    except ValueError as e:
        raise ValueError(f"Unknown puzzle type '{puzzle_type}'.") from e


    solver_instance = SolverClass(**init_params)
    
    result = solver_instance.solve()
    
    return result

def solver(puzzle_type: str, data: Dict[str, Any] = None, **kwargs) -> Any:
    # return solve(source=data, puzzle_type=puzzle_type, **kwargs)
    init_params = {}
    
    if isinstance(data, dict):
        init_params = data.copy()
    else:
        raise TypeError(f"Source must be dict or raw string, got {type(data)}")
    
    init_params.update(kwargs)

    try:
        SolverClass = get_solver_class(puzzle_type)
    except ValueError as e:
        raise ValueError(f"Unknown puzzle type '{puzzle_type}'.") from e
    return SolverClass(**init_params)


def decode(
    source: str,
    source_format: Optional[str] = None,
    converter_config: Optional[Dict[str, Any]] = None,
) -> PuzzleInstance:
    """
    Decode puzzle URL/text into PuzzleInstance (IR).

    Args:
        source: puzz.link URL, penpa URL, or penpa payload (`m=edit&p=...`).
        source_format: Optional explicit source format ('puzzlink' or 'penpa').
        converter_config: Optional converter config dict.
    """
    if not isinstance(source, str):
        raise TypeError(f"source must be str, got {type(source)}")

    fmt = _normalize_format_name(source_format) if source_format else _detect_source_format(source)
    if fmt == "ir":
        raise ValueError("decode(source_format='ir') is not valid.")

    converter = _build_converter(fmt, converter_config)
    normalized_source = _normalize_penpa_source(source) if fmt == "penpa" else source
    return converter.decode(normalized_source)


def encode(
    instance: PuzzleInstance,
    target_format: str,
    converter_config: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Encode PuzzleInstance (IR) into target format URL/text.

    Args:
        instance: PuzzleInstance IR.
        target_format: 'puzzlink' or 'penpa'.
        converter_config: Optional converter config dict.
    """
    if not isinstance(instance, PuzzleInstance):
        raise TypeError(f"instance must be PuzzleInstance, got {type(instance)}")

    fmt = _normalize_format_name(target_format)
    if fmt == "ir":
        raise ValueError("encode(target_format='ir') is not valid.")

    converter = _build_converter(fmt, converter_config)
    return converter.encode(instance)


def convert(
    source: Union[str, PuzzleInstance],
    target_format: str,
    source_format: Optional[str] = None,
    converter_config: Optional[Dict[str, Any]] = None,
    decode_converter_config: Optional[Dict[str, Any]] = None,
    encode_converter_config: Optional[Dict[str, Any]] = None,
) -> Union[str, PuzzleInstance]:
    """
    Convert between puzzlink/penpa/IR.

    Examples:
        - URL -> IR: convert(url, "ir")
        - puzzlink -> penpa: convert(url, "penpa")
        - penpa -> puzzlink: convert(url, "puzzlink")
        - IR -> puzzlink: convert(ir, "puzzlink")

    Notes:
        - `converter_config` is kept for backward compatibility and applies to both
          decode/encode when side-specific configs are not provided.
        - `decode_converter_config` and `encode_converter_config` let callers pass
          different settings per stage in a two-step conversion.
    """
    dst = _normalize_format_name(target_format)
    decode_cfg = decode_converter_config if decode_converter_config is not None else converter_config
    encode_cfg = encode_converter_config if encode_converter_config is not None else converter_config

    if isinstance(source, PuzzleInstance):
        if dst == "ir":
            return source
        return encode(source, dst, converter_config=encode_cfg)

    if not isinstance(source, str):
        raise TypeError(f"source must be str or PuzzleInstance, got {type(source)}")

    ir = decode(source, source_format=source_format, converter_config=decode_cfg)
    if dst == "ir":
        return ir
    return encode(ir, dst, converter_config=encode_cfg)

__all__ = ["solve", "solver", "decode", "encode", "convert"]
__version__ = '0.3.2'