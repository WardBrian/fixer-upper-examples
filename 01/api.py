from typing import Any, Tuple, Optional

class Checkpoint():
    ...


class Record():
    ...


def get_status() -> Checkpoint:
    ...


def get_record(name: Any) -> Optional[Record]:
    ...


def rollback(checkpoint: Checkpoint) -> None:
    ...


def create_record(name: str) -> Tuple[Record, bool]:
    ...


def link_record(record: Record, other: Record) -> bool:
    ...


def unlink_all(record: Record) -> bool:
    ...


def decrement_waiting_time(record: Record) -> bool:
    ...


def reset_waiting_time(record: Record) -> bool:
    ...

