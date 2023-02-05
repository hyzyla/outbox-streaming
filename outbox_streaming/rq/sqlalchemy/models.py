import sqlalchemy as sa

from ...common.sqlachemy.base import Base, OutboxMixin


class OutboxRQModel(Base, OutboxMixin):
    __tablename__ = "outbox_rq"

    func = sa.Column(sa.Text(), nullable=False)
    args = sa.Column(sa.Text(), nullable=False)
    kwargs = sa.Column(sa.Text(), nullable=False)
