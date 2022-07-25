import sqlalchemy as sa

from ...common.sqlachemy.base import Base, OutboxMixin


class OutboxCeleryModel(Base, OutboxMixin):
    __tablename__ = "outbox_celery"

    name = sa.Column(sa.Text(), nullable=False)
    args = sa.Column(sa.JSON())
    kwargs = sa.Column(sa.JSON())
    options = sa.Column(sa.JSON())
