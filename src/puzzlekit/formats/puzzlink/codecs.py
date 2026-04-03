"""
Puzzlink format codecs - number and border encoders/decoders.

This module provides low-level codecs for the various number and border
encoding formats used by puzz.link puzzles.
"""

from typing import Dict, Any, List, Tuple, Union, Optional
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# Number16 Codec
# =============================================================================

class Number16Codec:
    """
    number16 format codec: variable-length base16 encoding with skip support.

    Encoding ranges:
    - 0-15:      single char 0-9, a-f
    - 16-255:    -XX (2 chars)
    - 256-4095:  +XXX (3 chars)
    - 4096-8191: =XXX (3 chars, offset 4096)
    - 8192-12287: %XXX (3 chars, offset 8192)
    - 12288-77775: *XXXX (4 chars, offset 12240)
    - 77776+:    $XXXXX (5 chars, offset 77776)
    - '?':       . (1 char)
    - skip:      g-z (skip 1-20 cells)
    """

    @staticmethod
    def _read_value(body_str: str, i: int) -> Tuple[Union[int, str, None], int]:
        """Read a single number16-encoded value at position i.

        Returns:
            (value, length) tuple. value is None if unreadable.
        """
        if i >= len(body_str):
            return None, 0

        char = body_str[i]

        if ('0' <= char <= '9') or ('a' <= char <= 'f'):
            return int(char, 16), 1

        elif char == '-':
            if i + 2 <= len(body_str):
                return int(body_str[i+1 : i+3], 16), 3
        elif char == '+':
            if i + 3 <= len(body_str):
                return int(body_str[i+1 : i+4], 16), 4
        elif char == '=':
            if i + 3 <= len(body_str):
                return int(body_str[i+1 : i+4], 16) + 4096, 4
        elif char == '%':
            if i + 3 <= len(body_str):
                return int(body_str[i+1 : i+4], 16) + 8192, 4
        elif char == '*':
            if i + 4 <= len(body_str):
                return int(body_str[i+1 : i+5], 16) + 12240, 5
        elif char == '$':
            if i + 5 <= len(body_str):
                return int(body_str[i+1 : i+6], 16) + 77776, 6
        elif char == '.':
            return '?', 1

        return None, 0

    @staticmethod
    def _encode_skip(count: int) -> str:
        """Encode skip count using g-z characters.

        g (base36=16) -> skip 1
        h (17) -> skip 2
        ...
        z (35) -> skip 20
        """
        result = []
        while count > 0:
            if count >= 20:
                result.append('z')
                count -= 20
            else:
                result.append(chr(ord('g') + count - 1))
                count = 0
        return ''.join(result)

    @staticmethod
    def _encode_value(val: Any) -> str:
        """Encode a single integer/'?' value to number16 format."""
        if val == '?':
            return '.'
        elif isinstance(val, int):
            if 0 <= val <= 15:
                return format(val, 'x')
            elif 16 <= val <= 255:
                return '-' + format(val, '02x')
            elif 256 <= val <= 4095:
                return '+' + format(val, '03x')
            elif 4096 <= val <= 8191:
                return '=' + format(val - 4096, '03x')
            elif 8192 <= val <= 12287:
                return '%' + format(val - 8192, '03x')
            elif 12288 <= val <= 77775:
                return '*' + format(val - 12240, '04x')
            else:  # val >= 77776
                return '$' + format(val - 77776, '05x')
        else:
            return '-'  # fallback for invalid values

    def decode(self, body: str) -> Dict[int, int]:
        """Decode number16 format to {position: value} dict.

        Args:
            body: The number16-encoded string

        Returns:
            Dict mapping position index to value (int or '?')
        """
        number_map = {}
        i = 0  # char cursor
        c = 0  # position counter

        while i < len(body):
            char = body[i]

            val, length = self._read_value(body, i)
            if val is not None:
                number_map[c] = val
                i += length
                c += 1
            elif 'g' <= char <= 'z':
                skip_count = int(char, 36) - 15
                c += skip_count
                i += 1
            else:
                i += 1

        return number_map

    def encode(self, number_map: Dict[int, Any], max_id: int) -> str:
        """Encode number map to number16 format string.

        Args:
            number_map: Dict mapping position index to value (int or '?')
            max_id: Maximum position ID to encode up to

        Returns:
            number16-encoded string
        """
        if not number_map:
            return ""

        result = []
        current_id = 0
        skip_count = 0

        while current_id <= max_id:
            if current_id in number_map:
                if skip_count > 0:
                    result.append(self._encode_skip(skip_count))
                    skip_count = 0

                result.append(self._encode_value(number_map[current_id]))
            else:
                skip_count += 1

            current_id += 1

        if skip_count > 0:
            result.append(self._encode_skip(skip_count))

        return ''.join(result)


# =============================================================================
# Number4 Codec
# =============================================================================

class Number4Codec:
    """
    number4 format codec: values 0-4 with skip encoding.

    Encoding table:
    - '.'      -> '?'
    - '0'..'4' -> value 0..4
    - '5'..'9' -> value 0..4 + skip 1
    - 'a'..'e' -> value 0..4 + skip 2
    - 'g'..'z' -> skip 1..20
    """

    def decode(self, body: str) -> Dict[int, Union[int, str]]:
        """Decode number4 format to {position: value} dict."""
        number_map = {}
        pos = 0

        for char in body:
            if char == '.':
                number_map[pos] = '?'
            elif '0' <= char <= '4':
                number_map[pos] = int(char)
            elif '5' <= char <= '9':
                number_map[pos] = int(char) - 5
                pos += 1
            elif 'a' <= char <= 'e':
                number_map[pos] = int(char, 16) - 10
                pos += 2
            elif 'g' <= char <= 'z':
                pos += int(char, 36) - 16

            pos += 1

        return number_map

    def encode(self, number_map: Dict[int, Union[int, str]]) -> str:
        """Encode number map to number4 format string."""
        if not number_map:
            return ""

        max_pos = max(number_map.keys())
        result: List[str] = []
        pos = 0

        while pos <= max_pos:
            if pos not in number_map:
                skip_count = 0
                while pos <= max_pos and pos not in number_map and skip_count < 20:
                    skip_count += 1
                    pos += 1
                result.append(chr(ord("g") + skip_count - 1))
                continue

            val = number_map[pos]
            if val == "?":
                result.append(".")
                pos += 1
                continue

            n = int(val)
            if not (0 <= n <= 4):
                pos += 1
                continue

            next_missing = (pos + 1 <= max_pos and (pos + 1) not in number_map)
            next2_missing = (
                pos + 2 <= max_pos
                and (pos + 1) not in number_map
                and (pos + 2) not in number_map
            )

            if next2_missing:
                result.append(chr(ord("a") + n))  # a-e
                pos += 3
            elif next_missing:
                result.append(str(n + 5))         # 5-9
                pos += 2
            else:
                result.append(str(n))             # 0-4
                pos += 1

        return "".join(result)


# =============================================================================
# Number3 Codec
# =============================================================================

class Number3Codec:
    """
    number3 format codec: packs 3 trits (0/1/2) into one base36 character.

    Each character encodes: a*9 + b*3 + c where a,b,c are trits.
    """

    @staticmethod
    def _int_to_base36(val: int) -> str:
        """Convert integer 0-35 to base36 character."""
        if 0 <= val <= 9:
            return str(val)
        return chr(ord("a") + val - 10)

    def decode(self, body: str, max_iter: int = -1) -> List[int]:
        """Decode number3 format to list of trits (0/1/2).

        Args:
            body: The number3-encoded string
            max_iter: Maximum number of characters to decode (-1 for all)

        Returns:
            List of trits (0/1/2), length = chars_decoded * 3
        """
        number_list = []

        for char in body:
            if max_iter == 0:
                break

            num = int(char, 36)
            number_list.extend([
                (num // 9) % 3,
                (num // 3) % 3,
                (num // 1) % 3
            ])

            max_iter -= 1

        return number_list

    def encode(self, number_list: List[int]) -> str:
        """Encode list of trits to number3 format string.

        Args:
            number_list: List of trits (0/1/2)

        Returns:
            number3-encoded string
        """
        if not number_list:
            return ""

        result: List[str] = []
        i = 0
        while i < len(number_list):
            a = number_list[i] if i < len(number_list) else 0
            b = number_list[i + 1] if i + 1 < len(number_list) else 0
            c = number_list[i + 2] if i + 2 < len(number_list) else 0
            packed = a * 9 + b * 3 + c
            result.append(self._int_to_base36(packed))
            i += 3

        return "".join(result)


# =============================================================================
# Number36 Codec (decode only)
# =============================================================================

class Number36Codec:
    """
    number36 format codec: simple base36 encoding.

    Used for decoding only in some puzzle types.
    """

    def decode(self, body: str, max_iter: int = -1) -> List[Union[int, str]]:
        """Decode number36 format to list of values.

        Args:
            body: The number36-encoded string
            max_iter: Maximum iterations (-1 for all)

        Returns:
            List of decoded values
        """
        number_list = []
        index = 0

        while index < len(body) and max_iter != 0:
            char = body[index]

            if char == '-':
                if index + 2 < len(body):
                    number_list.append(int(body[index+1:index+3], 36))
                    index += 3
                else:
                    break
            elif char == '%':
                number_list.append('?')
                index += 1
            elif char == '.':
                number_list.append(' ')
                index += 1
            else:
                number_list.append(int(char, 36))
                index += 1

            max_iter -= 1

        return number_list


# =============================================================================
# Border Codec
# =============================================================================

class BorderCodec:
    """
    Border format codec: bit-packed base32 encoding.

    Each border is represented as 1 bit (present/absent).
    Every 5 bits are packed into one base32 character.
    """

    _BIT_MASKS = [16, 8, 4, 2, 1]  # 5-bit mask for extraction

    @staticmethod
    def _int_to_base32(val: int) -> str:
        """Convert integer 0-31 to base32 character (0-9, a-v)."""
        if 0 <= val <= 9:
            return str(val)
        elif 10 <= val <= 31:
            return chr(ord('a') + val - 10)
        else:
            raise ValueError(f"Value {val} out of range for base32 (0-31)")

    @staticmethod
    def _base32_to_int(char: str) -> int:
        """Convert base32 character to integer 0-31."""
        return int(char, 32)

    def decode(self, body: str, num_rows: int, num_cols: int) -> Tuple[Dict[int, int], int]:
        """Decode border string to {border_id: 1} dict.

        Args:
            body: The base32-encoded border string
            num_rows: Number of rows in the grid
            num_cols: Number of columns in the grid

        Returns:
            Tuple of (border_dict, consumed_length)
        """
        border_list = {}
        id_counter = 0

        # Calculate border counts
        num_vert_borders = (num_cols - 1) * num_rows
        num_horiz_borders = num_cols * (num_rows - 1)

        # Calculate string length (ceil division by 5)
        pos1 = (num_vert_borders + 4) // 5
        pos2 = pos1 + (num_horiz_borders + 4) // 5

        # Extract relevant portion
        border_str = body[:pos2]

        # Parse vertical borders
        for i in range(pos1):
            if i >= len(border_str):
                break
            val = self._base32_to_int(border_str[i])

            for w in range(5):
                if id_counter < num_vert_borders:
                    if val & self._BIT_MASKS[w]:
                        border_list[id_counter] = 1
                    id_counter += 1

        # Parse horizontal borders
        start_horiz_id = num_vert_borders
        id_counter = start_horiz_id

        for i in range(pos1, pos2):
            if i >= len(border_str):
                break
            val = self._base32_to_int(border_str[i])

            for w in range(5):
                if id_counter < start_horiz_id + num_horiz_borders:
                    if val & self._BIT_MASKS[w]:
                        border_list[id_counter] = 1
                    id_counter += 1

        return border_list, pos2

    def encode(self, border_list: Dict[int, int], num_rows: int, num_cols: int) -> str:
        """Encode border dict to base32 string.

        Args:
            border_list: Dict mapping border ID to 1 (or truthy value)
            num_rows: Number of rows in the grid
            num_cols: Number of columns in the grid

        Returns:
            base32-encoded border string
        """
        num_vert_borders = (num_cols - 1) * num_rows
        num_horiz_borders = num_cols * (num_rows - 1)
        total_borders = num_vert_borders + num_horiz_borders

        # Build bit array
        bits = [0] * total_borders
        for border_id in border_list:
            if 0 <= border_id < total_borders:
                bits[border_id] = 1

        result_chars = []

        # Encode vertical borders
        for i in range(0, num_vert_borders, 5):
            val = 0
            for w in range(5):
                if i + w < num_vert_borders and bits[i + w]:
                    val |= self._BIT_MASKS[w]
            result_chars.append(self._int_to_base32(val))

        # Encode horizontal borders
        for i in range(num_vert_borders, total_borders, 5):
            val = 0
            for w in range(5):
                if i + w < total_borders and bits[i + w]:
                    val |= self._BIT_MASKS[w]
            result_chars.append(self._int_to_base32(val))

        return ''.join(result_chars)


# =============================================================================
# Yajilin Arrow Codec
# =============================================================================

class YajilinArrowCodec:
    """
    Yajilin/Castle arrow format codec.

    Encodes arrow directions and associated numbers.
    """

    def decode(self, body: str, parsing_castle: bool = False) -> Dict[int, List[Any]]:
        """Decode yajilin/castle arrow format.

        Args:
            body: The arrow-encoded string
            parsing_castle: If True, parse castle-specific format with shading

        Returns:
            Dict mapping position to [direction, value, shading]
        """
        arrows = {}
        i = 0
        c = 0
        shading = 0

        while i < len(body):
            ca = body[i]
            if 'a' <= ca <= 'z':
                c += int(ca, 36) - 9
                i += 1
                continue

            if parsing_castle:
                shading = int(ca)
                i += 1
                ca = body[i]

            # Handle special case: '.' means direction=0, no number (empty clue)
            if ca == '.':
                arrows[c] = [0, "", shading]
                c += 1
                i += 1
                continue

            number_length = 3 if ca == '-' else 1
            if ca == '-':
                i += 1
                ca = body[i]

            direc = int(ca)
            number_length += direc // 5

            cell_value = body[i + 1:i + 1 + number_length]
            if cell_value == '.':
                cell_value = ""
            else:
                cell_value = str(int(cell_value, 16))

            arrows[c] = [direc % 5, cell_value, shading]
            c += 1
            i += number_length + 1

        return arrows


# =============================================================================
# Tapa Codec
# =============================================================================

class TapaCodec:
    """
    Tapa format encode/decode core.

    Scheme: pzprjs/tapa.js - direct port from Penpa+ implementation.

    Encoding:
    - '0'-'8':  single digit [0]-[8]
    - '9':      [1,1,1,1] special case
    - '.':      empty clue [-2]
    - 2-char (a-f + 0-z): 2/3/4 number combinations
    - 'g'-'z':  skip N cells (1-20)

    2-number: val = max(0,n1)*6 + max(0,n2) + 360, range [360,395] -> "a0"-"az"
    3-number: val = max(0,n1)*16 + max(0,n2)*4 + max(0,n3) + 396, range [396,459] -> "b0"-"cp"
    4-number: val = b1*8 + b2*4 + b3*2 + b4 + 460 (bi=1 if ni>0), range [460,475] -> "cq"-"d7"
    """

    STRINGS = "?12345"  # For decoding: index 0='?', 1-5='1'-'5'

    def encode_qnums(self, qnums: List[int]) -> Optional[str]:
        """Encode single qnums list to string (no skip)."""
        if not qnums:
            return None

        # Single digit or empty
        if len(qnums) == 1:
            return "." if qnums[0] == -2 else str(qnums[0])

        # Special case [1,1,1,1] -> "9"
        if len(qnums) == 4 and qnums == [1, 1, 1, 1]:
            return "9"

        # 2-number: each normalized to 0-5
        if len(qnums) == 2:
            n1, n2 = max(0, qnums[0]), max(0, qnums[1])
            if n1 <= 5 and n2 <= 5:
                return self._to_base36_2(n1 * 6 + n2 + 360)

        # 3-number: each normalized to 0-3
        if len(qnums) == 3:
            n1, n2, n3 = [max(0, q) for q in qnums]
            if n1 <= 3 and n2 <= 3 and n3 <= 3:
                return self._to_base36_2(n1 * 16 + n2 * 4 + n3 + 396)

        # 4-number: binary presence flags
        if len(qnums) == 4:
            bits = [1 if q > 0 else 0 for q in qnums]
            return self._to_base36_2(bits[0]*8 + bits[1]*4 + bits[2]*2 + bits[3] + 460)

        return None

    def encode(self, qnums_map: Dict[int, List[int]], max_id: int) -> str:
        """Encode qnums dict to puzzlink string."""
        if not qnums_map:
            return ""

        result: List[str] = []
        current_id = 0
        skip_count = 0

        while current_id <= max_id:
            if current_id in qnums_map:
                if skip_count > 0:
                    result.append(self._encode_skip(skip_count))
                    skip_count = 0
                encoded = self.encode_qnums(qnums_map[current_id])
                if encoded:
                    result.append(encoded)
            else:
                skip_count += 1
            current_id += 1

        if skip_count > 0:
            result.append(self._encode_skip(skip_count))

        return ''.join(result)

    def _encode_skip(self, count: int) -> str:
        """Encode skip: g(16)=skip1 ... z(35)=skip20."""
        result = []
        while count > 0:
            if count >= 20:
                result.append('z')
                count -= 20
            else:
                result.append(chr(ord('g') + count - 1))
                count = 0
        return ''.join(result)

    @staticmethod
    def _to_base36_2(val: int) -> str:
        """Convert 0-1295 to 2-char base36."""
        high, low = val // 36, val % 36
        return (str(high) if high <= 9 else chr(ord("a") + high - 10)) + \
               (str(low) if low <= 9 else chr(ord("a") + low - 10))

    def decode(self, body: str, num_rows: int, num_cols: int) -> Dict[int, List[int]]:
        """Decode puzzlink string to {position: qnums} dict."""
        qnums_map: Dict[int, List[int]] = {}
        i, c = 0, 0
        max_cells = num_rows * num_cols

        while i < len(body) and c < max_cells:
            char = body[i]

            # Single digit or special chars
            if '0' <= char <= '8':
                qnums_map[c] = [int(char)]
                i += 1
                c += 1
            elif char == '9':
                qnums_map[c] = [1, 1, 1, 1]
                i += 1
                c += 1
            elif char == '.':
                qnums_map[c] = [-2]
                i += 1
                c += 1
            # 2-char encoding (a-f + next)
            elif 'a' <= char <= 'f' and i + 1 < len(body):
                num = int(char + body[i + 1], 36)
                qnums = self._decode_2char(num)
                if qnums:
                    qnums_map[c] = qnums
                    i += 2
                    c += 1
                else:
                    i += 1
            # Skip g-z
            elif 'g' <= char <= 'z':
                c += int(char, 36) - 15
                i += 1
            else:
                i += 1

        return qnums_map

    def _decode_2char(self, num: int) -> Optional[List[int]]:
        """Decode 2-char base36 number to qnums."""
        # 2-number: 360-395 -> "a0"-"az"
        if 360 <= num < 396:
            val = num - 360
            n1, n2 = val // 6, val % 6
            return [n1 if n1 > 0 else -2, n2 if n2 > 0 else -2]
        # 3-number: 396-459 -> "b0"-"cp"
        if 396 <= num < 460:
            val = num - 396
            return [
                (val // 16) or -2,
                ((val % 16) // 4) or -2,
                (val % 4) or -2
            ]
        # 4-number: 460-475 -> "cq"-"d7"
        if 460 <= num < 476:
            val = num - 460
            return [
                1 if val & 4 else -2,
                1 if val & 8 else -2,
                1 if val & 2 else -2,
                1 if val & 1 else -2
            ]
        return None
