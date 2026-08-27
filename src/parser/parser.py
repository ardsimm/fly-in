from enum import StrEnum
from typing import Dict, List, Tuple, Union

from typing_extensions import TypedDict

from src.models import Connection, Map, Node

from .parser_exception import ParsingError


class MetadataValueType(StrEnum):
    STRING = "string"
    INT = "int"


class MetadataFieldTypedDict(TypedDict):
    name: str
    type: MetadataValueType


class Parser:

    def __split_line(self, line: str) -> List[str]:
        splitted_line: List[str] = []
        curr_part = ""
        in_metadata = False
        for char in line:
            if char == "[":
                in_metadata = True
            if char != " " or in_metadata:
                curr_part += char
            else:
                splitted_line.append(curr_part)
                curr_part = ""
        splitted_line.append(curr_part)
        return splitted_line

    def __strip_metadata_line(self, line: str) -> str:
        if not line.startswith("[") or not line.endswith("]"):
            raise ParsingError(
                "Parsing error: metadata should be surrounded with []"
                + "\nExample of expected value: \"[zone=normal color=red]\""
                + f"\ngot: {line}"
            )
        return line[1:len(line) - 1]

    def __split_metadata_fields(
        self,
        line: str,
        expected_fields: List[MetadataFieldTypedDict]
    ) -> List[List[str]]:
        splitted_fields = [
            field.split("=") for field in line.split(" ") if field != ""
        ]
        if (
            any(
                len(splitted_field) != 2
                for splitted_field
                in splitted_fields
            )
            or any(
                splitted_field[0] not in [
                    field["name"]
                    for field in expected_fields
                ]
                for splitted_field in splitted_fields
            )
        ):
            print(splitted_fields)
            raise ParsingError(
                f"Parsing error: invalid metadata: [{line}]"
                + "\nExample: ["
                + " ".join([
                    f'{field["name"]}=[value]'
                    for field in expected_fields
                ])
                + "]"
            )
        return splitted_fields

    def __parse_metadata_value(
        self,
        field_name: str,
        field_value: str,
        expected_fields: List[MetadataFieldTypedDict]
    ) -> Union[str, int]:
        expected_field = next(
            field_dict
            for field_dict in expected_fields
            if field_dict["name"] == field_name
        )
        type = expected_field["type"]
        parsed_value: Union[str, int]
        try:
            if type == MetadataValueType.STRING:
                parsed_value = field_value
            else:
                parsed_value = int(field_value)
        except ValueError:
            raise ParsingError(
                "Parsing error: Error in metadata:"
                + f" invalid type for field {field_name} " +
                "(expected value of type: ["
                + next(
                    expected_field
                    for expected_field
                    in expected_fields
                    if expected_field['name'] == field_name
                )['type'].name
                + "])"
            )
        return parsed_value

    def __parse_metadata(
        self,
        line: str,
        expected_fields: List[MetadataFieldTypedDict]
    ) -> Dict[str, Union[str, int]]:
        line = self.__strip_metadata_line(line)
        splitted_fields = self.__split_metadata_fields(line, expected_fields)
        metadata_dict: Dict[str, Union[str, int]] = {}
        for field in splitted_fields:
            field_name = field[0]
            field_value = field[1]
            metadata_dict[field[0]] = self.__parse_metadata_value(
                field_name=field_name,
                field_value=field_value,
                expected_fields=expected_fields
            )
        return metadata_dict

    def __split_hub_line(
        self,
        line: str,
        expected_prefix: str,
        example: str
    ) -> List[str]:
        splitted_line: List[str] = self.__split_line(line)
        splitted_len = len(splitted_line)
        if (
            splitted_len < 5
            or splitted_len > 6
            or splitted_line[0] != expected_prefix
        ):
            raise ParsingError(
                f"Parsing error: invalid \"{expected_prefix}\" line"
                + f"\nExpected example: \"{example}\""
                + f"\nGot: \"{line}\""
            )
        return splitted_line

    def __extract_zone(self, metadata: Dict[str, Union[str, int]]) -> str:
        zone = metadata.get("zone") or "normal"
        assert isinstance(zone, str)
        return zone

    def __extract_color(self, metadata: Dict[str, Union[str, int]]) -> str:
        color = metadata.get("color") or "none"
        assert isinstance(color, str)
        return color

    def __extract_max_drones(
        self,
        metadata: Dict[str, Union[str, int]]
    ) -> int:
        max_drones = metadata.get("max_drones") or 1
        assert isinstance(max_drones, int)
        return max_drones

    def __map_priority(self, zone: str, hub_name: str) -> int:
        mapped_priorities = {
            "blocked": -1,
            "restricted": 0,
            "normal": 1,
            "priority": 2
        }
        priority = mapped_priorities.get(zone)
        if priority is None:
            raise ParsingError(
                f"Parsing error: invalid zone {zone} for hub {hub_name}"
                + ", valid options are: "
                + f"[{', '.join(list(mapped_priorities.keys()))}]"
            )
        return priority

    def __parse_coordinate(
        self,
        value: str
    ) -> int:
        assert value is not None
        parsed_value: int
        try:
            parsed_value = int(value)
        except ValueError:
            raise ParsingError(
                "Parsing error: invalid value: "
                + f"{value}"
                + " for hub y"
            )
        return parsed_value

    def __parse_hub(
        self,
        line: str,
        expected_prefix: str,
        example: str = "hub: {name} {x} {y} [zone={zone_type} color={color}]",
    ) -> Node:
        splitted_line = self.__split_hub_line(line, expected_prefix, example)

        hub_name = splitted_line[1]
        hub_x = splitted_line[2]
        hub_y = splitted_line[3]

        if len(splitted_line) > 5:
            hub_metadata = splitted_line[4]
        else:
            hub_metadata = None

        if hub_metadata is not None:
            metadata = self.__parse_metadata(
                line=hub_metadata,
                expected_fields=[{
                    "name": "zone",
                    "type": MetadataValueType.STRING
                }, {
                    "name": "color",
                    "type": MetadataValueType.STRING
                }, {
                    "name": "max_drones",
                    "type": MetadataValueType.INT
                }]
            )
        else:
            metadata = {}

        return Node(
            name=hub_name,
            color=self.__extract_color(metadata),
            x=self.__parse_coordinate(
                hub_x
            ),
            y=self.__parse_coordinate(
                hub_y
            ),
            max_drones=self.__extract_max_drones(metadata),
            priority=self.__map_priority(
                zone=self.__extract_zone(metadata),
                hub_name=hub_name
            ),
            connections=[]
        )

    def __parse_nb_drones(self, line: str) -> int:
        splitted_line = line.split(" ")
        if len(splitted_line) != 2 or splitted_line[0] != "nb_drones:":
            raise ParsingError(
                "Parsing error: invalid nb_drones lines,"
                + "\nexample: \"nb_drones: 5\""
            )
        try:
            n = int(splitted_line[1])
            return n
        except ValueError as e:
            raise ParsingError(
                f"Parsing error: invalid nb_drones lines: {e}"
                + "\nexample: \"nb_drones: 5\""
            )

    def __parse_start_hub(self, line: str) -> Node:
        return self.__parse_hub(
            line=line,
            expected_prefix="start_hub:",
            example="start_hub: hub {x} {y} [color={color}]"
        )

    def __parse_end_hub(self, line: str) -> Node:
        return self.__parse_hub(
            line=line,
            expected_prefix="end_hub:",
            example="end_hub: hub {x} {y} [color={color}]"
        )

    def __parse_hubs(self, lines: List[str]) -> List[Node]:
        hubs: List[Node] = []
        for line in lines:
            hubs.append(
                self.__parse_hub(
                    line=line,
                    expected_prefix="hub:",
                )
            )
        return hubs

    def __split_connection_line(self, line: str) -> List[str]:
        splitted_line = self.__split_line(line)
        splitted_line_len = len(splitted_line)
        if splitted_line_len < 2 or splitted_line_len > 3:
            raise ParsingError(
                "Parsing error: invalid connection format: "
                + line
                + "\nExpected example: \"connection: {hub1}-{hub1}"
                + " [{metadata (optional)}]\""
                + f"\nGot: \"{line}\""
            )
        return splitted_line

    def __extract_hub_names(
        self,
        splitted_line: List[str],
        available_hubs: List[Node]
    ) -> Tuple[str, str]:
        available_hub_names = [
            available_hub.name
            for available_hub in available_hubs
        ]
        (hub1_name, hub2_name) = splitted_line[1].split("-")
        if hub1_name not in available_hub_names:
            raise ParsingError(
                f"Hub name {hub1_name} is invalid,"
                + " options: " + f"[{', '.join(available_hub_names)}]"
                + f" got line: {' '.join(splitted_line)}"
            )
        if hub2_name not in available_hub_names:
            raise ParsingError(
                f"Hub name {hub2_name} is invalid,"
                + " options: " + f"[{', '.join(available_hub_names)}]"
            )
        return (hub1_name, hub2_name)

    def __extract_max_link_capacity(
        self,
        metadata: Dict[str, Union[str, int]]
    ) -> int:
        max_link_capacity = metadata.get("max_link_capacity") or 1
        assert isinstance(max_link_capacity, int)
        if max_link_capacity < 1:
            raise ParsingError(
                "Parsing error: link must have a capacity >= 1"
            )
        return max_link_capacity

    def __parse_connections(
        self,
        lines: List[str],
        available_hubs: List[Node]
    ) -> List[Connection]:
        connections: List[Connection] = []
        for line in lines:
            if not line.startswith("connection: "):
                raise ParsingError(
                    "Parsing error: connection lines must start with"
                    + "\"connection: \""
                )
            splitted_line = self.__split_connection_line(line)

            (hub1_name, hub2_name) = self.__extract_hub_names(
                splitted_line=splitted_line,
                available_hubs=available_hubs
            )

            if len(splitted_line) > 2:
                metadata_string = splitted_line[2]
            else:
                metadata_string = None

            if metadata_string is not None:
                metadata = self.__parse_metadata(
                    line=metadata_string,
                    expected_fields=[
                        {
                            "name": "max_link_capacity",
                            "type": MetadataValueType.INT
                        }
                    ]
                )
            else:
                metadata = {}

            connections.append(
                Connection(
                    capacity=self.__extract_max_link_capacity(
                        metadata=metadata
                    ),
                    nodes=[
                        next(
                            hub
                            for hub in available_hubs
                            if hub.name == hub1_name
                        ),
                        next(
                            hub
                            for hub in available_hubs
                            if hub.name == hub2_name
                        )
                    ]
                )
            )
        return connections

    def __filter_lines(self, lines: List[str], prefix: str) -> List[str]:
        return [
            line
            for line in lines
            if line.startswith(prefix)
        ]

    def __get_nb_drones_line(self, lines: List[str]) -> str:
        filtered = self.__filter_lines(lines, "nb_drones: ")
        if len(filtered) < 1:
            raise ParsingError("File misses a nb_drones line")
        if len(filtered) > 1:
            raise ParsingError("File has > 1 nb_drones lines")
        return filtered[0]

    def __get_start_hub_line(self, lines: List[str]) -> str:
        filtered = self.__filter_lines(lines, "start_hub: ")
        if len(filtered) < 1:
            raise ParsingError("File misses a start_hub line")
        if len(filtered) > 1:
            raise ParsingError("File has > 1 start_hub lines")
        return filtered[0]

    def __get_end_hub_line(self, lines: List[str]) -> str:
        filtered = self.__filter_lines(lines, "end_hub: ")
        if len(filtered) < 1:
            raise ParsingError("File misses a end_hub line")
        if len(filtered) > 1:
            raise ParsingError("File has > 1 end_hub lines")
        return filtered[0]

    def __get_hub_lines(self, lines: List[str]) -> List[str]:
        return self.__filter_lines(lines, "hub: ")

    def __get_connection_lines(self, lines: List[str]) -> List[str]:
        return self.__filter_lines(lines, "connection: ")

    def __strip_line(self, line: str) -> str:
        if "#" not in line:
            return line.strip()
        return line[:line.index("#")].strip()

    def __strip_lines(self, lines: List[str]) -> List[str]:
        stripped_lines: List[str] = []
        for line in lines:
            stripped_line = self.__strip_line(line)
            if (
                not stripped_line.startswith("#")
                and stripped_line != "\n"
                and stripped_line != ""
            ):
                stripped_lines.append(stripped_line)
        return stripped_lines

    def parse(self, map_content: str) -> Map:

        try:
            lines = self.__strip_lines(map_content.split("\n"))

            nb_drones = self.__parse_nb_drones(
                self.__get_nb_drones_line(lines)
            )
            entry_point = self.__parse_start_hub(
                self.__get_start_hub_line(lines)
            )
            exit_point = self.__parse_end_hub(self.__get_end_hub_line(lines))
            nodes = self.__parse_hubs(self.__get_hub_lines(lines))
            connections = self.__parse_connections(
                lines=self.__get_connection_lines(lines),
                available_hubs=[entry_point] + [exit_point] + nodes
            )

            for node in nodes + [entry_point] + [exit_point]:
                for connection in connections:
                    if node in connection.nodes:
                        node.connections.append(connection)

            return Map(
                nb_drones=nb_drones,
                entry_point=entry_point,
                exit_point=exit_point,
                nodes=nodes,
                connections=connections
            )
        except AssertionError as e:
            raise ParsingError(e)
