from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship
from src.core.database import Base


class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    cooperativa_id = Column(
        Integer,
        ForeignKey("cooperatives.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    origin_id = Column(
        Integer,
        ForeignKey("localities.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    destination_id = Column(
        Integer,
        ForeignKey("localities.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    name = Column(String(200), nullable=False)
    name_suffix = Column(String(30), nullable=True)
    distance_km = Column(Numeric(8, 2), nullable=False)
    estimated_time_minutes = Column(Integer, nullable=False)
    description = Column(String(100), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    cooperativa = relationship("Cooperativa")
    origin = relationship("Locality", foreign_keys=[origin_id])
    destination = relationship("Locality", foreign_keys=[destination_id])
    stops = relationship(
        "RouteStop",
        back_populates="route",
        cascade="all, delete-orphan",
        order_by="RouteStop.stop_order",
        lazy="selectin",
    )
    adoptions = relationship(
        "CooperativaGeneralRoute",
        back_populates="route",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        CheckConstraint("origin_id <> destination_id", name="ck_routes_origin_destination_diff"),
        CheckConstraint("distance_km > 0", name="ck_routes_distance_positive"),
        CheckConstraint(
            "estimated_time_minutes >= 1 AND estimated_time_minutes <= 1439",
            name="ck_routes_time_range",
        ),
        Index(
            "uq_general_routes_origin_dest_dist",
            origin_id,
            destination_id,
            distance_km,
            unique=True,
            postgresql_where=(cooperativa_id.is_(None)),
            sqlite_where=(cooperativa_id.is_(None)),
        ),
        Index(
            "uq_coop_routes_coop_origin_dest_dist",
            cooperativa_id,
            origin_id,
            destination_id,
            distance_km,
            unique=True,
            postgresql_where=(cooperativa_id.isnot(None)),
            sqlite_where=(cooperativa_id.isnot(None)),
        ),
    )


class RouteStop(Base):
    __tablename__ = "route_stops"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(
        Integer,
        ForeignKey("routes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    locality_id = Column(
        Integer,
        ForeignKey("localities.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    stop_order = Column(Integer, nullable=False)

    route = relationship("Route", back_populates="stops")
    locality = relationship("Locality", lazy="selectin")

    __table_args__ = (
        UniqueConstraint("route_id", "stop_order", name="uq_route_stops_route_order"),
        UniqueConstraint("route_id", "locality_id", name="uq_route_stops_route_locality"),
        CheckConstraint("stop_order >= 1", name="ck_route_stops_order_positive"),
    )


class CooperativaGeneralRoute(Base):
    __tablename__ = "cooperativa_general_routes"

    id = Column(Integer, primary_key=True, index=True)
    cooperativa_id = Column(
        Integer,
        ForeignKey("cooperatives.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    route_id = Column(
        Integer,
        ForeignKey("routes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    cooperativa = relationship("Cooperativa")
    route = relationship("Route", back_populates="adoptions", lazy="selectin")

    __table_args__ = (
        UniqueConstraint("cooperativa_id", "route_id", name="uq_coop_general_routes_coop_route"),
    )
