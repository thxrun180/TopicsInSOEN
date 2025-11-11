from logforge.readers import read_log_file
from logforge.analytics import summarize_log

SAMPLE = """\
INFO | 2025-11-11T10:00:00 | User logged in | tags=auth,user
WARN | 2025-11-11T10:01:00 | Disk  space  low | tags=sys
INFO | 2025-11-11T10:02:00 | User logged in | tags=auth
ERROR | 2025-11-11T10:03:00 | Cannot connect to DB | tags=db,sys
"""

def test_pipeline(tmp_path):
    p = tmp_path/"a.log"
    p.write_text(SAMPLE, encoding="utf-8")
    entries = read_log_file(str(p))
    r = summarize_log(entries, top_n=2)

    assert r["levels"]["INFO"] == 2
    assert r["levels"]["WARN"] == 1
    assert r["levels"]["ERROR"] == 1
    # tags: auth=2, user=1, sys=2, db=1
    assert r["tags"]["auth"] == 2
    assert r["tags"]["sys"] == 2
    # top messages should normalize double spaces
    assert r["top"][0][0] in {"User logged in", "Disk space low"}
    assert len(r["unique_msgs_per_level"]) == 3
