from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


SQLALCHEMY_DATABASE_URL = "sqlite:///./city-navigator-prototype.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Node(Base):
    __tablename__ = "NODES"
    id = Column("ID", Integer, primary_key=True)
    name = Column("NAME", String(length=50), nullable=False)


class Edge(Base):
    __tablename__ = "EDGES"
    id = Column("ID", Integer, primary_key=True, index=True)
    distance_min = Column("DISTANCE_MIN", Integer, nullable=False)
    start_node_id = Column("START_NODE_ID", Integer, ForeignKey("NODES.ID"), nullable=False)
    end_node_id = Column("END_NODE_ID", Integer, ForeignKey("NODES.ID"), nullable=False)
    start_node = relationship("Node", foreign_keys="Edge.start_node_id")
    end_node = relationship("Node", foreign_keys="Edge.end_node_id")



def main() -> None:
    try:
        db = SessionLocal()

        print()
        nodes = db.query(Node).all()
        for single_node in nodes:
            print(f"id={single_node.id} name={single_node.name}")

        print()
        edges = db.query(Edge).all()
        for single_edge in edges:
            print(f"{single_edge.start_node.name} -> {single_edge.end_node.name} ({single_edge.distance_min} min)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
