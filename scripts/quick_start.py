import puzzlekit
import time
import os
import logging

# Script-only logging configuration:
# - Library code never calls `basicConfig`.
# - Enable logs by setting `PUZZLEKIT_LOG_LEVEL` (e.g. DEBUG/INFO/WARNING).
_level_name = os.getenv("PUZZLEKIT_LOG_LEVEL", "").strip().upper()
if _level_name:
    _level = getattr(logging, _level_name, None)
    if isinstance(_level, int):
        logging.basicConfig(
            level=_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

# Raw input data
start_time = time.time()
problem_str = """
10 10\n6 5 - - - - - - - -\n- - - - - - - - - -\n- - - - - 2 - - - -\n1 - - - - - 9 - - -\n- - - - - - - - - -\n- - - - - - - - - -\n3 - - - - - 8 - - -\n- 4 - - - - - - - -\n- - - - - - - - - -\n- - 7 - - - - - - -\n1 4 4 4 4 4 4 4 4 4\n1 1 1 4 4 4 8 4 4 4\n1 1 1 1 4 8 8 8 8 4\n2 2 2 7 7 7 9 9 9 9\n2 3 3 3 7 7 7 9 9 9\n2 3 3 3 7 7 7 10 9 9\n3 3 5 3 7 6 10 10 9 9\n3 5 5 5 5 6 10 10 10 10\n3 5 5 6 6 6 6 10 10 10\n3 5 6 6 6 6 6 10 10 10
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="shimaguni")

# Print solution grid
print(res.solution_data.get('solution_grid', []))
print(res.solution_data.get('cpu_time', "Not available"))
print(res.solution_data.get('build_time', "Not available"))
end_time = time.time()
print(f"Time taken: {end_time - start_time} seconds")
# Visualize (optional)
# res.show()


# URL -> IR
ir = puzzlekit.decode("https://puzz.link/p?slither/10/10/g188227cl1dg367bdcg3ddgbhdgd1agbd760dg2cl633661d")
# IR -> penpa
penpa_url = puzzlekit.encode(ir, "penpa")
print(penpa_url)
# get:
# m=edit&p=7VdtT9swEP7Or0...


penpa_url = "https://swaroopg92.github.io/penpa-edit/#m=edit&p=7Vfvb+I4EP3OX3Hy17WOOIFgIq1OlP6QqrZXru31CkKVISZJawibhLZK1f99Zxyq2IGudHfSqiedQoaZ9+zxTGKeRf5tIzJJmYMfj1P4hqvDuL5d7uvb2V7XSaFk8AsdbIo4zcCJi2KdB+32elOOy/GvKlk9tte/5SopYpm1mYOfGfdF5PMwYm5vFvmuUGHEQxHyWRQq1w+jnuvO9QDOZyGlvx8f04VQuaSndw8Hh4+D56PBX+3u2PNuLhZfHg5HNw/h7Z9s5CTtzLlQfHV+eXigvpyU4/N48CSPpH+Zp/NYSRGKcnx7+qJWxzyKF2x4Gg/5Qqyc/Bu/7j8djL5+bU22rU1br2U/KAe0PAkmxCOUMLhdMqXlKHgtzwMyT5ezhNDyCnhC2ZSS5UYVyTxVaUbesfIMPJjpgntUu7eaR29YgcwB/2Lrg3sH7jzJ5kren1XIZTAprynBAg70bHTJMn2SuBgWh3FVFAAzUcCryeNkTagHRL4J08fNdiibvtFy8A/agEzvbaBbtYHenjawu3/dhgwj+bKng/707Q3e0B/Qw30wwXZuapfX7lXwCvYieCWeA1NxL8N0yOZ5EHp12LXZHoS49auwY7MdZOu5nb4VdjFzPbjLIXTrEAfXoc+swb69kI8L1YN7rlUVx7n1utwuo2+z/Y41lzk2zRzkzdi3KmGswbvYZV0ac7FNY7x+3MZ4D+cb4z3Mb8Z2q6yDvZpxo54Ormfk7zbW04/diP0G72N+I59+8u88bBmmN86dtsfautpew76ipaftobaOtl1tz/SYI21vtR1q29HW12N6uDP/1t79CeVMvEro7av738OmrQm52mQLMZegJcN0uU7zpJAE9JzkqbrPK+5evoh5QYLqXDEZC1ttljMJMmhAKk3XcKzty/BOWWASrdJM7qUQRIH7IBVSe1LN0ixs1PQslLJ70ae4BVUybEFFBhprxCLL0mcLWYoitgDjWLEyyVXjYRbCLlE8isZqy/pxvLXIC9E3/AThR///4fv5D198W85nk7HPVo7e6Gn2A9WpySa8R3sA/YH8GOw+/AOlMdgmviMrWOyusgC6R1wAbeoLQLsSA+COygD2gdBg1qbWYFVNucGldhQHlzJFZ0K2f0zwbwqZtr4D"
puzzlink_url = puzzlekit.convert(penpa_url, "puzzlink")
print(puzzlink_url)
# get:
# https://puzz.link/p?slither/10/10/b86ag68dg127bg62aldg8dad8bgdl26dg722cg68dg88b3