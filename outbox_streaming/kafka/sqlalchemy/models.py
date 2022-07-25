import sqlalchemy as sa

from ...common.sqlachemy.base import Base, OutboxMixin


class OutboxKafkaModel(Base, OutboxMixin):
    __tablename__ = "outbox_kafka"

    topic = sa.Column(sa.Text(), nullable=False)
    value = sa.Column(sa.LargeBinary())
    key = sa.Column(sa.Text())
