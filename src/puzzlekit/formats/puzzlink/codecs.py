"""
Puzzlink format codecs - number and border encoders/decoders.

This module provides low-level codecs for the various number and border
encoding formats used by puzz.link puzzles.
"""

from typing import Dict, Any, List, Tuple, Union
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
