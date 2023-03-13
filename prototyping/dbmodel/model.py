from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


SQLALCHEMY_DATABASE_URL = "sqlite:///./prototyping/dbmodel/city-navigator-prototype.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class MeansOfTransport(Base):
    __tablename__ = "MEANS_OF_TRANSPORT"
    id = Column("ID", Integer, primary_key=True)
    identifier = Column("IDENTIFIER", String(length=20), nullable=False)


class Node(Base):
    __tablename__ = "NODES"
    id = Column("ID", Integer, primary_key=True)
    name = Column("NAME", String(length=50), nullable=False)


class Edge(Base):
    __tablename__ = "EDGES"
    id = Column("ID", Integer, primary_key=True)
    distance_min = Column("DISTANCE_MIN", Integer, nullable=False)
    start_node_id = Column("START_NODE_ID", Integer, ForeignKey("NODES.ID"), nullable=False)
    end_node_id = Column("END_NODE_ID", Integer, ForeignKey("NODES.ID"), nullable=False)
    line_id = Column("LINE_ID", Integer, ForeignKey("LINES.ID"), nullable=False)
    start_node = relationship("Node", foreign_keys="Edge.start_node_id")
    end_node = relationship("Node", foreign_keys="Edge.end_node_id")
    line = relationship("Line", foreign_keys="Edge.line_id")


class LineItineraryEntry(Base):
    __tablename__ = "LINE_ITINERARY_ENTRIES"
    id = Column("ID", Integer, primary_key=True)
    edge_id = Column("EDGE_ID", Integer, ForeignKey("EDGES.ID"), nullable=True)
    next_entry_id = Column("NEXT_ENTRY_ID", Integer, ForeignKey("LINE_ITINERARY_ENTRIES.ID"), nullable=False)
    next_entry = relationship("LineItineraryEntry", foreign_keys="LineItineraryEntry.next_entry_id")


class Line(Base):
    __tablename__ = "LINES"
    id = Column("ID", Integer, primary_key=True, index=True)
    label = Column("LABEL", String, nullable=False)
    means_of_transport_id = Column("MEANS_OF_TRANSPORT_ID", Integer, ForeignKey("MEANS_OF_TRANSPORT.ID"), nullable=False)
    means_of_transport = relationship("MeansOfTransport", foreign_keys="Line.means_of_transport_id")
    itinerary_start_direction_one_id = Column("ITINERARY_START_DIRECTION_ONE_ID", Integer, ForeignKey("LINE_ITINERARY_ENTRIES.ID"), nullable=False)
    itinerary_start_direction_two_id = Column("ITINERARY_START_DIRECTION_TWO_ID", Integer, ForeignKey("LINE_ITINERARY_ENTRIES.ID"), nullable=False)
    itinerary_start_direction_one = relationship("LineItineraryEntry", foreign_keys="Line.itinerary_start_direction_one_id")
    itinerary_start_direction_two = relationship("LineItineraryEntry", foreign_keys="Line.itinerary_start_direction_two_id")


def main() -> None:
    try:
        db = SessionLocal()

        print()
        print("Nodes")
        nodes = db.query(Node).all()
        for single_node in nodes:
            print(f"id={single_node.id} name={single_node.name}")

        print()
        print("Node by name")
        node = db.query(Node).filter(Node.name == "Simmering").first()
        print(f"id={node.id} name={node.name}")


        print()
        print("Edges")
        edges = db.query(Edge).all()
        for single_edge in edges:
            print(f"{single_edge.start_node.name} -> {single_edge.end_node.name} ({single_edge.distance_min} min)")

        print()
        print("Lines")
        lines = db.query(Line).all()
        for single_line in lines:
            print(f"label={single_line.label} means of transport={single_line.means_of_transport.identifier}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
