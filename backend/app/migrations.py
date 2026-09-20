"""启动时数据库修补：为 flush_harvests 补建 (room_id, flush_no) 唯一索引。

历史库可能已经存在叠号数据，直接 CREATE UNIQUE INDEX 会失败，
因此先按 (room_id, flush_no) 分组去重（保留最早一笔），再建唯一索引。
幂等：已建过索引的库不会重复执行。
"""

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.database import engine

UNIQUE_INDEX_NAME = "uix_flush_room_no"


def _index_exists(conn, table: str, index: str) -> bool:
    if engine.dialect.name == "sqlite":
        # 命名索引在 sqlite_master 里；建表内联的 UNIQUE 约束只会生成自动索引，
        # 得用 PRAGMA 看 (room_id, flush_no) 上是否已有唯一索引。
        named = conn.execute(
            text("SELECT 1 FROM sqlite_master WHERE type = 'index' AND name = :i LIMIT 1"),
            {"i": index},
        ).first()
        if named is not None:
            return True
        for row in conn.execute(text(f"PRAGMA index_list('{table}')")).fetchall():
            # 列序: seq, name, unique, origin, partial
            if len(row) >= 3 and row[2] == 1:
                cols = [
                    c[2]
                    for c in conn.execute(
                        text(f"PRAGMA index_info('{row[1]}')")
                    ).fetchall()
                ]
                if cols == ["room_id", "flush_no"]:
                    return True
        return False
    else:
        row = conn.execute(
            text(
                "SELECT 1 FROM information_schema.statistics "
                "WHERE table_schema = DATABASE() AND table_name = :t AND index_name = :i "
                "LIMIT 1"
            ),
            {"t": table, "i": index},
        ).first()
    return row is not None


def _table_exists(conn, table: str) -> bool:
    if engine.dialect.name == "sqlite":
        row = conn.execute(
            text("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = :t LIMIT 1"),
            {"t": table},
        ).first()
    else:
        row = conn.execute(
            text(
                "SELECT 1 FROM information_schema.tables "
                "WHERE table_schema = DATABASE() AND table_name = :t LIMIT 1"
            ),
            {"t": table},
        ).first()
    return row is not None


def _dedupe_flush_harvests(conn) -> None:
    """删掉同室同潮次的重复行，保留 id 最小（最早录入）的一笔。

    子查询再包一层派生表，绕开 MySQL “不能在 DELETE 的子查询里直接引用目标表”
    的限制；SQLite 同样支持该写法。
    """
    result = conn.execute(
        text(
            "DELETE FROM flush_harvests WHERE id NOT IN ("
            "  SELECT min_id FROM ("
            "    SELECT MIN(id) AS min_id FROM flush_harvests"
            "    GROUP BY room_id, flush_no"
            "  ) AS keepers"
            ")"
        )
    )
    if result.rowcount and result.rowcount > 0:
        print(f"Deduped {result.rowcount} duplicate flush_harvests row(s).")


def ensure_flush_unique_index() -> None:
    """幂等地确保唯一索引存在；已有叠号数据时先去重再建，保证启动不被卡住。"""
    try:
        with engine.begin() as conn:
            if _index_exists(conn, "flush_harvests", UNIQUE_INDEX_NAME):
                return
            if not _table_exists(conn, "flush_harvests"):
                return
            _dedupe_flush_harvests(conn)
            conn.execute(
                text(
                    f"CREATE UNIQUE INDEX {UNIQUE_INDEX_NAME} "
                    "ON flush_harvests (room_id, flush_no)"
                )
            )
            print(f"Created unique index {UNIQUE_INDEX_NAME} on flush_harvests.")
    except DBAPIError:
        # 多进程同时启动时可能竞态：另一个 worker 已抢先建索引。
        # 再确认一次，索引确已存在即视为成功，否则照常抛出。
        with engine.connect() as conn:
            if not _index_exists(conn, "flush_harvests", UNIQUE_INDEX_NAME):
                raise
            print(f"Unique index {UNIQUE_INDEX_NAME} already created by another worker.")
