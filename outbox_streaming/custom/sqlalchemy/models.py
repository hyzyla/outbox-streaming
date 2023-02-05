import sqlalchemy as sa

from ...common.sqlachemy.base import Base, OutboxMixin


class OutboxCustomModel(Base, OutboxMixin):
    __tablename__ = "outbox_custom"

    value = sa.Column(sa.LargeBinary())
