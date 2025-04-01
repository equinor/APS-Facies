# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "lxml",
#     "types-lxml",
#     "typer",
# ]
# ///

from __future__ import annotations

import base64
from abc import ABC
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Self, NewType, cast
from collections.abc import Mapping

import typer
import lxml.etree as ET
from lxml.etree import _Element
from zipfile import ZipFile

app = typer.Typer(pretty_exceptions_show_locals=False)


class Format(str, Enum):
    html = 'html'


OId = NewType('OId', str)


@app.command()
def main(file: Path, format: Format = Format.html, destination: Path = Path('out')):
    """
    Extracts the content of a MindManager file to a hierarchical structure in plain text.

    file: str: The path to the MindManager file.
    """
    mind_manager = MindManager.from_file(file)

    match format:
        case 'html':
            exporter = HTMLExporter(mind_manager)
        case _:
            raise NotImplementedError(f'{format} is not supported')
    exporter.export(destination)


def get_oid(element: _Element) -> OId:
    return cast(OId, element.attrib['OId'])


class Exporter(ABC):
    def export(self, destination: Path) -> None: ...


class HTMLExporter(Exporter):
    def __init__(self, mind_manager: MindManager):
        self.mind_manager = mind_manager

    @staticmethod
    def compose_topic_body(topic: Topic) -> str:
        body = topic.notes.body
        if '<img ' in body:
            for source in topic.notes.image_data:
                image = topic.notes.image_data[source]
                body = body.replace(
                    source,
                    f'data:image/png; base64, {base64.b64encode(image.data).decode()}',
                )
        return body

    def export(self, destination: Path) -> None:
        hierarchy = self.export_topics(destination)
        self.export_links(destination, hierarchy)

    def export_topics(self, destination: Path) -> dict[str | None, Path]:
        topics = self._indexed(self.mind_manager.topics)
        hierarchy: dict[str | None, Path] = {
            self.mind_manager.oid: destination,
        }
        while topics:
            topic, index = topics.pop(0)
            destination = hierarchy[topic.oid] = (
                hierarchy[topic.parent.oid] / f'{index + 1} - {topic.text}'
            )
            destination.mkdir(parents=True, exist_ok=True)
            if topic.notes:
                with open(destination / 'index.html', 'w') as f:
                    f.write(self.compose_topic_body(topic))
            topics.extend(self._indexed(topic.children))
        return hierarchy

    def export_links(self, destination: Path, hierarchy: dict[str | None, Path]):
        links_destination = destination / 'links'
        links_destination.mkdir(parents=True, exist_ok=True)

        for idx, relationship in enumerate(self.mind_manager.relationships):
            from_node, to_node = relationship.connections
            from_path = hierarchy[from_node.object_reference]
            to_path = hierarchy[to_node.object_reference]
            topic = relationship.topic
            destination = links_destination / f'{idx + 1} - {topic.text}'
            destination.mkdir(parents=True, exist_ok=True)
            with open(destination / 'index.html', 'w') as f:
                f.write(self.compose_topic_body(topic))
            self._link(destination / 'linked-from', from_path)
            self._link(destination / 'linked-to', to_path)
            self._link(from_path / 'links-to', destination / 'index.html')
            self._link(to_path / 'links-from', destination / 'index.html')

    @staticmethod
    def _link(from_path: Path, to_path: Path):
        with open(from_path, 'w') as f:
            f.write(str(to_path))

    @staticmethod
    def _indexed(topics: list[Topic]):
        return [
            (topic, index) for topic, index in zip(topics.copy(), range(len(topics)))
        ]


@dataclass
class MindManager:
    oid: OId
    topics: list[Topic]
    relationships: list[Relationship]

    @classmethod
    def from_file(cls, file: str | Path) -> Self:
        with ZipFile(file) as archive:
            root: _Element = ET.XML(archive.read('Document.xml'))
            oid = get_oid(root)
            one_topic: _Element = root.find('ap:OneTopic', root.nsmap)
            if one_topic is None:
                raise RuntimeError(
                    f"Empty mind manager document; missing 'OneTopic' in {file}"
                )
            topics = [Topic.from_xml(topic, archive) for topic in one_topic]
            relationships = [
                Relationship.from_xml(relationship, archive)
                for relationship in root.find('ap:Relationships', root.nsmap)
            ]
            cls.assert_found_all_topics(topics, relationships, root)
        instance = cls(
            oid=oid,
            topics=topics,
            relationships=relationships,
        )
        for topic in instance.topics:
            topic.parent = instance
        return instance

    @staticmethod
    def assert_found_all_topics(
        topics: list[Topic], relationships: list[Relationship], root: _Element
    ):
        """Reality check if all ap:Topic-s have been included"""
        all_topics = root.xpath('//*/ap:Topic', namespaces=root.nsmap)
        num_topics = sum(len(topic) for topic in topics) + len(relationships)
        if num_topics != len(all_topics):
            raise RuntimeError(
                f'Number of topics in relationships ({num_topics}) does not match number of topics in document ({len(all_topics)})'
            )


@dataclass
class Relationship:
    oid: OId
    connections: list[Connection]
    topic: Topic

    @classmethod
    def from_xml(cls, element: _Element, archive: ZipFile) -> Self:
        oid = get_oid(element)
        connections = [
            Connection.from_xml(connection)
            for connection in element.findall('ap:ConnectionGroup', element.nsmap)
        ]
        connections.sort(key=lambda c: c.index)
        if len(connections) != 2:
            raise NotImplementedError
        topics = [
            Topic.from_xml(topic, archive)
            for topic in element.find('ap:FloatingTopics', element.nsmap).findall(
                'ap:Topic', element.nsmap
            )
        ]
        if len(topics) != 1:
            raise NotImplementedError
        return cls(
            oid=oid,
            connections=connections,
            topic=topics[0],
        )


@dataclass
class Connection:
    index: int
    cx: float
    cy: float
    end_point_cx: float
    end_point_cy: float
    object_reference: OId

    @classmethod
    def from_xml(cls, element: _Element) -> Self:
        index = int(element.get('Index'))
        connections: list[_Element] = element.findall('ap:Connection', element.nsmap)
        if len(connections) != 1:
            raise RuntimeError(f'Expected 1 connection, found {len(connections)}')
        connection = connections[0]
        cx = float(connection.get('CX'))
        cy = float(connection.get('CY'))
        end_point_cx = float(connection.get('EndPointCX'))
        end_point_cy = float(connection.get('EndPointCY'))
        object_reference: OId = cast(
            OId, connection.find('ap:ObjectReference', element.nsmap).get('OIdRef')
        )
        return cls(
            index=index,
            cx=cx,
            cy=cy,
            end_point_cx=end_point_cx,
            end_point_cy=end_point_cy,
            object_reference=object_reference,
        )


@dataclass
class Topic:
    oid: OId
    text: str
    color: str
    notes: Notes
    children: list[Topic]
    parent: Topic | MindManager = None

    def __post_init__(self):
        for child in self.children:
            child.parent = self

    @classmethod
    def from_xml(cls, element: _Element, archive: ZipFile) -> Self:
        oid = get_oid(element)
        text = element.find('ap:Text', namespaces=element.nsmap).get('PlainText')
        color_element = element.find('ap:Color', namespaces=element.nsmap)
        if color_element is not None:
            color = color_element.get('FillColor')
        else:
            color = None
        notes = Notes.from_xml(
            element.find('ap:NotesGroup', namespaces=element.nsmap), archive
        )
        if (
            sub_topics := element.find('ap:SubTopics', namespaces=element.nsmap)
        ) is not None:
            children = [
                Topic.from_xml(topic, archive) for topic in sub_topics.getchildren()
            ]
        else:
            children = []
        return cls(
            oid=oid,
            text=text,
            color=color,
            notes=notes,
            children=children,
        )

    def __len__(self):
        return sum(len(child) for child in self.children) + 1


@dataclass
class Notes:
    preview_text: str
    body: str
    image_data: Images

    @classmethod
    def from_xml(cls, element: _Element, archive: ZipFile) -> Self | None:
        if element is None:
            return None
        notes_element: _Element = element.findall('ap:NotesXhtmlData', element.nsmap)
        if len(notes_element) != 1:
            raise NotImplementedError
        notes_element = notes_element[0]
        preview_text = notes_element.get('PreviewPlainText')
        html_tag: _Element = notes_element.find('.//{*}html')
        body = ET.tostring(html_tag, encoding='unicode', method='html')
        image_data = Images.from_xml(element, archive)

        return cls(
            preview_text=preview_text,
            body=body,
            image_data=image_data,
        )


@dataclass
class Image:
    data: bytes
    uri: str

    @classmethod
    def from_xml(cls, element: _Element, archive: ZipFile) -> Self:
        uri: str = element.find('cor:Uri', element.nsmap).text
        if uri.startswith('mmarch://'):
            path = uri.removeprefix('mmarch://')
            image = archive.read(path)
        else:
            raise NotImplementedError
        return cls(
            data=image,
            uri=uri,
        )


class Images(Mapping[str, Image]):
    def __iter__(self):
        return self._file_mapping.__iter__()

    def __len__(self):
        return self._file_mapping.__len__()

    def __getitem__(self, key, /):
        return self._file_mapping.__getitem__(key)

    def __init__(self, image_mapping: dict[str, Image | None]):
        self._file_mapping = image_mapping

    @classmethod
    def from_xml(cls, element: _Element, archive: ZipFile) -> Self:
        image_data = {}
        for image in element.findall('ap:NotesData', element.nsmap):
            image_uri: str = image.attrib['ImageUri']
            image_data[image_uri] = Image.from_xml(image, archive)
        return cls(image_data)


if __name__ == '__main__':
    app()
