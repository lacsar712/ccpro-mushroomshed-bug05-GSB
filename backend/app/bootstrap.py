"""幂等的建表与历史数据修复。

启动流程：``Base.metadata.create_all`` 建表（新库会直接带上
``(room_id, flush_no)`` 唯一约束）；对老库则先清理历史叠号数据，
再补上同名的唯一索引。整个过程可重复执行。
"""

from sqlalchemy import inspect, text

from app import models  # noqa: F401  # 确保所有模型注册到 metadata
from app.database import Base, engine

UNIQUE_INDEX_NAME = "uq_flush_harvest_room_flush"
TARGET_COLUMNS = {"room_id", "flush_no"}


def _room_flush_unique_exists(insp) -> bool:
    indexes = insp.get_indexes("flush_harvests") if insp.has_table("flush_harvests") else []
    for idx in indexes:
        if idx.get("unique") and set(idx.get("column_names") or []) == TARGET_COLUMNS:
            return True
    for con in insp.get_unique_constraints("flush_harvests"):
        if set(con.get("column_names") or []) == TARGET_COLUMNS:
            return True
    return False


def ensure_flush_harvest_unique_index() -> None:
    """保证 flush_harvests 上存在 (room_id, flush_no) 唯一索引。

    老库可能已经有叠号数据，唯一索引无法直接建立：先把同室同潮次的
    多余记录删掉（保留最早一笔 MIN(id)，并打印日志），再建索引。
    """
    insp = inspect(engine)
    if _room_flush_unique_exists(insp):
        return

    print(
        "FlushHarvest: 缺少 (room_id, flush_no) 唯一限制，"
        "先清理历史叠号记录再补建唯一索引……"
    )
    with engine.begin() as conn:
        removed = conn.execute(
            text(
                "DELETE FROM flush_harvests WHERE id NOT IN ("
                " SELECT keep_id FROM ("
                " SELECT MIN(id) AS keep_id FROM flush_harvests"
                " GROUP BY room_id, flush_no"
                " ) AS keepers)"
            )
        )
        removed_count = removed.rowcount or 0
        if removed_count:
            print(
                f"FlushHarvest: 已删除 {removed_count} 条历史叠号记录"
                "（同室同潮次保留最早的一笔）。"
            )
        # MySQL 8 与 SQLite 均支持该语法；MySQL 的 DDL 会隐式提交前面的清理
        conn.execute(
            text(
                f"CREATE UNIQUE INDEX {UNIQUE_INDEX_NAME} "
                "ON flush_harvests (room_id, flush_no)"
            )
        )
    print("FlushHarvest: (room_id, flush_no) 唯一索引已就绪。")


def init_schema() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_flush_harvest_unique_index()


if __name__ == "__main__":
    init_schema()
