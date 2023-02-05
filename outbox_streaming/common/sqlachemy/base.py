import copy
from typing import Any

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class OutboxMixin:

    __table__: sa.Table
    metadata: sa.MetaData

    id = sa.Column(sa.BigInteger(), sa.Identity(), primary_key=True, nullable=False)
    created_at = sa.Column(sa.DateTime(), server_default=sa.func.now())

    def to_dict(self) -> dict[str, Any]:
        value = copy.deepcopy(self.__dict__)
        value.pop("_sa_instance_state", None)
        return value

    @classmethod
    def consume_query(cls, size: int) -> Any:
        return (
            sa.delete(cls)
            .where(
                # TODO: autodetect primary key
                cls.id.in_(
                    sa.select(cls.id)
                    .select_from(cls)
                    .order_by(cls.id.asc())
                    .limit(size)
                    .with_for_update()
                )
            )
            .returning(cls)
        )
