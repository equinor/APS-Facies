# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "PyYAML",
#     "lxml",
#     "types-lxml",
#     "typer",
#     "beautifulsoup4",
# ]
# ///

from __future__ import annotations

import base64
import hashlib
from abc import ABC
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable, NewType, Self, TypeAlias, cast
from zipfile import ZipFile

import lxml.etree as ET
import typer
import yaml
from bs4 import BeautifulSoup, PageElement, Tag
from lxml.etree import _Element

app = typer.Typer(pretty_exceptions_show_locals=False)


class Format(str, Enum):
    html = 'html'
    markdown = 'markdown'


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
        case 'markdown':
            exporter = MarkdownExporter(mind_manager)
        case _:
            raise NotImplementedError(f'{format} is not supported')
    exporter.export(destination)


def get_oid(element: _Element) -> OId:
    return cast(OId, element.attrib['OId'])


class Exporter(ABC):
    def export(self, destination: Path) -> None: ...


class MarkdownExporter(Exporter):
    def __init__(self, mind_manager: MindManager):
        self.mind_manager = mind_manager

    def export(self, destination: Path) -> None:
        hierarchy = ExportHelper.export_topics(
            self.mind_manager,
            destination,
            lambda hierarchy, index, topic: hierarchy[topic.parent.oid]
            / topic.text.replace('\n', '').strip(),
            lambda topic: 'README.md',
            lambda hierarchy, topic: self.export_topic(hierarchy, topic),
        )
        # TODO: Deal with links
        root = {}
        for path in hierarchy.values():
            path = path.relative_to(destination)
            tree = root
            for part in path.parts:
                if part not in tree:
                    tree[part] = {
                        '_name': str(path / 'README.md'),
                    }
                else:
                    tree = tree[part]

        with open(destination / 'mkdocs.yml', 'w') as f:
            f.write(yaml.dump(root, sort_keys=False))

    def export_topic(self, hierarchy: Hierarchy, topic: Topic) -> str:
        soup = BeautifulSoup(topic.notes.body, 'lxml')
        content = f"""---
title: {topic.text}
---
"""
        for tag in soup.body:
            content += self._export_tag(hierarchy, topic, tag)
        return content.replace('\xc2', '').replace('\xa0', '')

    def _export_tag(
        self, hierarchy: Hierarchy, topic: Topic, tag: Tag | PageElement
    ) -> str:
        if tag.name == 'p':
            parts = []
            for content in tag.contents:
                if isinstance(content, str):
                    parts.append(content)
                elif isinstance(content, Tag):
                    parts.append(self._export_tag(hierarchy, topic, content))
                else:
                    raise NotImplementedError(
                        f'Unsupported content type: {type(content)}'
                    )
            return '\n'.join(parts)
        elif tag.name == 'ul':
            return '\n'.join(
                self._export_tag(hierarchy, topic, item) for item in tag.contents
            )
        elif tag.name == 'li':
            # TODO: Deal with depth / nested lists
            return f'- {"".join(str(item) for item in tag.contents)}\n'
        elif tag.name == 'img':
            return f'![]({self._export_image(hierarchy, topic, tag)})'
        elif tag.name == 'font':
            # Handle font tags, which may contain color information
            color = tag.get('color')
            if color:
                return f"<span style='color: {color};'>{''.join(str(item) for item in tag.contents)}</span>"
            else:
                return ''.join(str(item) for item in tag.contents)
        elif tag.name in ['b', 'strong']:
            return f'**{"".join(str(item) for item in tag.contents)}**'
        elif tag.name in ['i', 'em']:
            return f'_{"".join(str(item) for item in tag.contents)}_'
        elif tag.name == 'ol':
            parts = []
            for index, item in enumerate(tag.contents, start=1):
                if isinstance(item, Tag):
                    parts.append(f'{index}. {self._export_tag(hierarchy, topic, item)}')
                else:
                    raise NotImplementedError(
                        f'Unsupported content type in ordered list: {type(item)}'
                    )
            return '\n'.join(parts)
        elif tag.name == 'br':
            return '\n'
        elif tag.name == 'span':
            return ''.join(str(item) for item in tag.contents)
        elif tag.name == 'blockquote':
            # TODO: Deal with nesting
            return '\n> '.join(
                self._export_tag(hierarchy, topic, element) for element in tag.contents
            )
        else:
            raise NotImplementedError(f'Unsupported tag: {tag.name}')

    def _export_image(self, hierarchy: Hierarchy, topic: Topic, tag: Tag) -> str:
        image_uri = tag.get('src')
        if not image_uri:
            raise ValueError("Image tag does not have a 'src' attribute")
        if image_uri.startswith('mmnotes://'):
            # TODO: Write image to disk, and return the appropriate path
            image_data = topic.notes.image_data[image_uri].data
            _hash = hashlib.sha3_256(image_data).hexdigest()
            file_name = f'{_hash}.png'
            with open(hierarchy[topic.oid] / file_name, 'wb') as f:
                f.write(image_data)
            return file_name
        else:
            raise NotImplementedError(f'Unsupported image URI: {image_uri}')


class HTMLExporter(Exporter):
    def __init__(self, mind_manager: MindManager):
        self.mind_manager = mind_manager

    @staticmethod
    def compose_topic_body(hierarchy: Hierarchy, topic: Topic) -> str:
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
        return ExportHelper.export_topics(
            self.mind_manager,
            destination,
            lambda hierarchy, index, topic: hierarchy[topic.parent.oid]
            / f'{index + 1} - {topic.text}',
            lambda topic: 'index.html',
            lambda topic: self.compose_topic_body(topic),
        )

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


Hierarchy: TypeAlias = dict[str | None, Path]


class ExportHelper:
    @classmethod
    def export_topics(
        cls,
        mind_manager: MindManager,
        destination: Path,
        file_path_func: Callable[[Hierarchy, int, Topic], Path],
        file_name_func: Callable[[Topic], str],
        file_content_func: Callable[[Hierarchy, Topic], str],
    ) -> Hierarchy:
        topics = cls._indexed(mind_manager.topics)
        hierarchy: Hierarchy = {
            mind_manager.oid: destination,
        }
        while topics:
            topic, index = topics.pop(0)
            destination = hierarchy[topic.oid] = file_path_func(hierarchy, index, topic)
            destination.mkdir(parents=True, exist_ok=True)
            if topic.notes:
                with open(destination / file_name_func(topic), 'w') as f:
                    f.write(file_content_func(hierarchy, topic))
            topics.extend(cls._indexed(topic.children))
        return hierarchy

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
        end_point_cx = float(connection.get('EndPointCX', 0))
        end_point_cy = float(connection.get('EndPointCY', 0))
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
