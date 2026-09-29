from enum import StrEnum
from typing import Dict, List, Optional, Tuple, Union

from typing_extensions import TypedDict

from src.enums.node_priority import NodePriority
from src.models import Connection, Drone, Map, Node

from .parser_exception import ParsingError


class MetadataValueType(StrEnum):
    """Types a metadata value can be parsed to."""

    STRING = "string"
    INT = "int"


class MetadataFieldTypedDict(TypedDict):
    """Description of an accepted metadata field.

    Attributes:
        name: Field name.
        type: Type the value is parsed to.
        ignore: Whether the field is accepted but discarded.
    """

    name: str
    type: MetadataValueType
    ignore: bool


class Parser:
    """Parser for the map file format."""

    def __split_line(self, line: str) -> List[str]:
        """Split a line on spaces, keeping a [...] block as one token.

        Args:
            line: Line to split.

        Returns:
            The tokens of the line.
        """
        splitted_line: List[str] = []
        curr_part = ""
        in_metadata = False
        for char in line:
            if char == "[":
                in_metadata = True
            if char == "]":
                in_metadata = False
            if char != " " or in_metadata:
                curr_part += char
            else:
                if curr_part.strip() != "":
                    splitted_line.append(curr_part)
                curr_part = ""
        if curr_part.strip() != "":
            splitted_line.append(curr_part)
        return splitted_line

    def __strip_metadata_line(self, line: str) -> str:
        """Remove the brackets around a metadata block.

        Args:
            line: Metadata block, brackets included.

        Returns:
            The content of the block.

        Raises:
            ParsingError: If the block is not surrounded by brackets.
        """
        if not line.startswith("[") or not line.endswith("]"):
            raise ParsingError(
                "Parsing error: metadata should be surrounded with []"
                + '\nExample of expected value: "[zone=normal color=red]"'
                + f"\ngot: {line}"
            )
        return line[1: len(line) - 1]

    def __split_metadata_fields(
        self, line: str, expected_fields: List[MetadataFieldTypedDict]
    ) -> List[List[str]]:
        """Split the content of a metadata block into key/value pairs.

        Args:
            line: Content of the block, without brackets.
            expected_fields: Accepted fields.

        Returns:
            One [key, value] list per field.

        Raises:
            ParsingError: If a field is malformed or not accepted.
        """
        splitted_fields = [
            field.split("=") for field in line.split(" ") if field != ""
        ]
        if any(
            len(splitted_field) != 2 for splitted_field in splitted_fields
        ) or any(
            splitted_field[0]
            not in [field["name"] for field in expected_fields]
            for splitted_field in splitted_fields
        ):
            raise ParsingError(
                f"Parsing error: invalid metadata: [{line}]"
                + "\nExample: ["
                + " ".join(
                    [f'{field["name"]}=[value]' for field in expected_fields]
                )
                + "]"
            )
        return splitted_fields

    def __parse_metadata_value(
        self,
        field_name: str,
        field_value: str,
        expected_fields: List[MetadataFieldTypedDict],
    ) -> Union[str, int]:
        """Convert a metadata value to the type of its field.

        Args:
            field_name: Name of the field.
            field_value: Raw value.
            expected_fields: Accepted fields.

        Returns:
            The converted value.

        Raises:
            ParsingError: If the value cannot be converted.
        """
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
                + f" invalid type for field {field_name} "
                + "(expected value of type: ["
                + next(
                    expected_field
                    for expected_field in expected_fields
                    if expected_field["name"] == field_name
                )["type"].name
                + "])"
            )
        return parsed_value

    def __parse_metadata(
        self, line: str, expected_fields: List[MetadataFieldTypedDict]
    ) -> Dict[str, Union[str, int]]:
        """Parse a metadata block.

        Args:
            line: Metadata block, brackets included.
            expected_fields: Accepted fields.

        Returns:
            The parsed values by field name, ignored fields excluded.

        Raises:
            ParsingError: If the block is invalid or a field is duplicated.
        """
        line = self.__strip_metadata_line(line)
        splitted_fields = self.__split_metadata_fields(line, expected_fields)
        metadata_dict: Dict[str, Union[str, int]] = {}
        field_occurences: Dict[str, int] = {}
        for field in splitted_fields:
            expected_field_names = [
                field.get("name") for field in expected_fields
            ]
            field_name = field[0]
            field_value = field[1]
            field_occurence = field_occurences.setdefault(field_name, 0)
            if field_occurence > 0:
                raise ParsingError(
                    f"Duplicated metadata field {field_name}"
                )
            field_occurences[field_name] += 1
            expected_field = next(
                iter(
                    [
                        field
                        for field in expected_fields
                        if field.get("name") == field_name
                    ]
                ),
                None,
            )
            if expected_field is None:
                raise ParsingError(
                    f"Unexpected metadata {field_name}, "
                    + f"options: {expected_field_names}"
                )
            if not expected_field.get("ignore"):
                metadata_dict[field[0]] = self.__parse_metadata_value(
                    field_name=field_name,
                    field_value=field_value,
                    expected_fields=expected_fields,
                )
        return metadata_dict

    def __split_hub_line(
        self, line: str, expected_prefix: str, example: str
    ) -> List[str]:
        """Split a hub line and check its prefix and token count.

        Args:
            line: Hub line.
            expected_prefix: Expected prefix, e.g. "hub:".
            example: Valid line shown in the error message.

        Returns:
            The tokens of the line.

        Raises:
            ParsingError: If the prefix or the number of tokens is wrong.
        """
        splitted_line: List[str] = self.__split_line(line)
        splitted_len = len(splitted_line)
        if (
            splitted_len < 4
            or splitted_len > 5
            or splitted_line[0] != expected_prefix
        ):
            raise ParsingError(
                f'Parsing error: invalid "{expected_prefix}" line'
                + f'\nExpected example: "{example}"'
                + f'\nGot: "{line}"'
            )
        return splitted_line

    def __extract_zone(
        self,
        metadata: Dict[str, Union[str, int]],
        allowed_values: Optional[List[str]] = None,
    ) -> str:
        """Get the zone type from parsed metadata.

        Args:
            metadata: Parsed metadata.
            allowed_values: Accepted zone types, all of them by default.

        Returns:
            The zone type, "normal" if unspecified.

        Raises:
            ParsingError: If the zone type is not accepted.
        """
        if allowed_values is None:
            allowed_values = ["normal", "restricted", "priority", "blocked"]
        zone = metadata.get("zone") or "normal"
        if zone not in allowed_values:
            raise ParsingError(
                f"Invalid zone {zone}, options:" + f"{allowed_values}"
            )
        assert isinstance(zone, str)
        return zone

    def __extract_color(self, metadata: Dict[str, Union[str, int]]) -> str:
        """Get the color from parsed metadata.

        Args:
            metadata: Parsed metadata.

        Returns:
            The color name, "none" if unspecified.
        """
        color = metadata.get("color") or "none"
        assert isinstance(color, str)
        return color

    def __extract_max_drones(
        self, metadata: Dict[str, Union[str, int]]
    ) -> int:
        """Get the zone capacity from parsed metadata.

        Args:
            metadata: Parsed metadata.

        Returns:
            The capacity, 1 if unspecified.

        Raises:
            ParsingError: If the capacity is lower than 1.
        """
        max_drones = metadata.get("max_drones")
        if max_drones is None:
            max_drones = 1
        assert isinstance(max_drones, int)
        if max_drones < 1:
            raise ParsingError(
                f"Invalid max drones {max_drones}:"
                + " max_drones must be an integer >= 1"
            )
        return max_drones

    def __map_priority(self, zone: str, hub_name: str) -> int:
        """Convert a zone type to its NodePriority value.

        Args:
            zone: Zone type.
            hub_name: Name of the hub, for the error message.

        Returns:
            The NodePriority value of the zone type.

        Raises:
            ParsingError: If the zone type is unknown.
        """
        mapped_priorities = {
            "blocked": NodePriority.blocked.value,
            "restricted": NodePriority.restricted.value,
            "normal": NodePriority.normal.value,
            "priority": NodePriority.priority.value,
        }
        priority = mapped_priorities.get(zone)
        if priority is None:
            raise ParsingError(
                f"Parsing error: invalid zone {zone} for hub {hub_name}"
                + ", valid options are: "
                + f"[{', '.join(list(mapped_priorities.keys()))}]"
            )
        return priority

    def __parse_coordinate(self, value: str) -> int:
        """Parse a hub coordinate.

        Args:
            value: Raw coordinate.

        Returns:
            The coordinate.

        Raises:
            ParsingError: If the coordinate is not an integer.
        """
        assert value is not None
        parsed_value: int
        try:
            parsed_value = int(value)
        except ValueError:
            raise ParsingError(
                "Parsing error: invalid value: "
                + f"{value}"
                + " for hub coordinate"
            )
        return parsed_value

    def __parse_hub(
        self,
        line: str,
        expected_prefix: str = "hub:",
        example: str = "hub: {name} {x} {y} [zone={zone_type} color={color}]",
        expected_metadata: Optional[List[MetadataFieldTypedDict]] = None,
    ) -> Node:
        """Parse a zone line.

        Args:
            line: Zone line.
            expected_prefix: Expected prefix of the line.
            example: Valid line shown in error messages.
            expected_metadata: Accepted metadata fields, those of "hub:" by
                default.

        Returns:
            The parsed zone, without connections.

        Raises:
            ParsingError: If the line is invalid.
        """
        if expected_metadata is None:
            expected_metadata = [
                {
                    "name": "zone",
                    "type": MetadataValueType.STRING,
                    "ignore": False,
                },
                {
                    "name": "color",
                    "type": MetadataValueType.STRING,
                    "ignore": False,
                },
                {
                    "name": "max_drones",
                    "type": MetadataValueType.INT,
                    "ignore": False,
                },
            ]

        splitted_line = self.__split_hub_line(line, expected_prefix, example)

        hub_name = splitted_line[1]
        if " " in hub_name or "-" in hub_name:
            raise ParsingError(
                f"Error in line: \"{line}\":\n"
                + f"Invalid name {hub_name}:"
                + " names cannot contain spaces or dashes"
            )

        try:
            hub_x = self.__parse_coordinate(splitted_line[2])
            hub_y = self.__parse_coordinate(splitted_line[3])
        except ParsingError as e:
            raise ParsingError(f"Error in line: \"{line}\":\n{e}")

        if len(splitted_line) >= 5:
            hub_metadata = splitted_line[4]
        else:
            hub_metadata = None

        if hub_metadata is not None:
            try:
                metadata = self.__parse_metadata(
                    line=hub_metadata, expected_fields=expected_metadata
                )
            except ParsingError as e:
                raise ParsingError(
                    f"Error in line: \"{line}\":\n{e}"
                )
        else:
            metadata = {}

        try:
            zone = self.__extract_zone(metadata)
            max_drones = self.__extract_max_drones(metadata)
        except ParsingError as e:
            raise ParsingError(f"Error in line: \"{line}\":\n{e}")

        return Node(
            name=hub_name,
            color=self.__extract_color(metadata),
            x=hub_x,
            y=hub_y,
            max_drones=max_drones,
            priority=self.__map_priority(zone=zone, hub_name=hub_name),
            connections=[],
        )

    def __parse_nb_drones(self, line: str) -> int:
        """Parse the nb_drones line.

        Args:
            line: nb_drones line.

        Returns:
            The number of drones.

        Raises:
            ParsingError: If the line is invalid or the number is below 1.
        """
        splitted_line = self.__split_line(line)
        if len(splitted_line) != 2 or splitted_line[0] != "nb_drones:":
            raise ParsingError(
                f'Error in line "{line}":\n'
                + "Parsing error: invalid nb_drones lines,"
                + '\nexample: "nb_drones: 5"'
            )
        try:
            n = int(splitted_line[1])
            if n < 1:
                raise ParsingError(
                    f'Error in line "{line}":\n'
                    + "nb_drones must be an integer >= 1"
                )
            return n
        except ValueError as e:
            raise ParsingError(
                f'Error in line "{line}":\n'
                + f"Parsing error: invalid nb_drones lines: {e}"
                + '\nexample: "nb_drones: 5"'
            )

    def __parse_start_hub(self, line: str) -> Node:
        """Parse the start_hub line, ignoring its max_drones.

        Args:
            line: start_hub line.

        Returns:
            The start hub.

        Raises:
            ParsingError: If the line is invalid.
        """
        return self.__parse_hub(
            line=line,
            expected_prefix="start_hub:",
            example="start_hub: hub {x} {y} [color={color}]",
            expected_metadata=[
                {
                    "name": "zone",
                    "type": MetadataValueType.STRING,
                    "ignore": False,
                },
                {
                    "name": "color",
                    "type": MetadataValueType.STRING,
                    "ignore": False,
                },
                {
                    "name": "max_drones",
                    "type": MetadataValueType.INT,
                    "ignore": True,
                },
            ],
        )

    def __parse_end_hub(self, line: str) -> Node:
        """Parse the end_hub line, ignoring its max_drones.

        Args:
            line: end_hub line.

        Returns:
            The end hub.

        Raises:
            ParsingError: If the line is invalid.
        """
        return self.__parse_hub(
            line=line,
            expected_prefix="end_hub:",
            example="end_hub: hub {x} {y} [color={color}]",
            expected_metadata=[
                {
                    "name": "zone",
                    "type": MetadataValueType.STRING,
                    "ignore": False,
                },
                {
                    "name": "color",
                    "type": MetadataValueType.STRING,
                    "ignore": False,
                },
                {
                    "name": "max_drones",
                    "type": MetadataValueType.INT,
                    "ignore": True,
                },
            ],
        )

    def __split_connection_line(self, line: str) -> List[str]:
        """Split a connection line and check its token count.

        Args:
            line: Connection line.

        Returns:
            The tokens of the line.

        Raises:
            ParsingError: If the number of tokens is wrong.
        """
        splitted_line = self.__split_line(line)
        splitted_line_len = len(splitted_line)
        if splitted_line_len < 2 or splitted_line_len > 3:
            raise ParsingError(
                f'Error in line "{line}":\n'
                + "Parsing error: invalid connection format: "
                + line
                + '\nExpected example: "connection: {hub1}-{hub1}'
                + ' [{metadata (optional)}]"'
                + f'\nGot: "{line}"'
            )
        return splitted_line

    def __extract_hub_names(
        self, splitted_line: List[str], available_hubs: List[Node]
    ) -> Tuple[str, str]:
        """Get the two zone names of a connection.

        Args:
            splitted_line: Tokens of the connection line.
            available_hubs: Zones defined so far.

        Returns:
            The names of the two connected zones.

        Raises:
            ParsingError: If a name is missing or not defined yet.
        """
        available_hub_names = [
            available_hub.name for available_hub in available_hubs
        ]
        splitted_hubs = splitted_line[1].split("-")
        if len(splitted_hubs) != 2:
            raise ParsingError(
                f"Error in line: \"{' '.join(splitted_line)}\":\n"
                + "Missing hub"
            )
        try:
            hub1_name, hub2_name = splitted_hubs
        except ValueError:
            raise ParsingError(
                f"Error in line: \"{' '.join(splitted_line)}\":\n"
                + "Invalid connection: Missing hubs or malformated field"
            )
        if hub1_name not in available_hub_names:
            raise ParsingError(
                f"Error in line: \"{' '.join(splitted_line)}\":\n"
                + f"Hub name {hub1_name} is invalid,"
                + " options: "
                + f"[{', '.join(available_hub_names)}]"
                + f" got line: {' '.join(splitted_line)}"
            )
        if hub2_name not in available_hub_names:
            raise ParsingError(
                f"Error in line: \"{' '.join(splitted_line)}\":\n"
                + f"Hub name {hub2_name} is invalid,"
                + " options: "
                + f"[{', '.join(available_hub_names)}]"
            )
        return (hub1_name, hub2_name)

    def __extract_max_link_capacity(
        self, metadata: Dict[str, Union[str, int]]
    ) -> int:
        """Get the link capacity from parsed metadata.

        Args:
            metadata: Parsed metadata.

        Returns:
            The capacity, 1 if unspecified.

        Raises:
            ParsingError: If the capacity is lower than 1.
        """
        max_link_capacity = metadata.get("max_link_capacity")
        if max_link_capacity is None:
            max_link_capacity = 1
        assert isinstance(max_link_capacity, int)
        if max_link_capacity < 1:
            raise ParsingError("Parsing error: link must have a capacity >= 1")
        return max_link_capacity

    def __parse_connection(
        self, line: str, available_hubs: List[Node]
    ) -> Connection:
        """Parse a connection line.

        Args:
            line: Connection line.
            available_hubs: Zones defined so far.

        Returns:
            The parsed connection.

        Raises:
            ParsingError: If the line is invalid or links a zone to itself.
        """
        splitted_line = self.__split_connection_line(line)

        hub1_name, hub2_name = self.__extract_hub_names(
            splitted_line=splitted_line, available_hubs=available_hubs
        )

        if hub1_name == hub2_name:
            raise ParsingError(
                f"Error in line: \"{line}\":\n"
                + f"This implementation does not accept self-loops ({
                    hub1_name
                }-{
                    hub2_name
                })"
            )

        if len(splitted_line) > 2:
            metadata_string = splitted_line[2]
        else:
            metadata_string = None

        if metadata_string is not None:
            try:
                metadata = self.__parse_metadata(
                    line=metadata_string,
                    expected_fields=[
                        {
                            "name": "max_link_capacity",
                            "type": MetadataValueType.INT,
                            "ignore": False,
                        }
                    ],
                )
            except ParsingError as e:
                raise ParsingError(
                    f"Error in line: \"{line}\":\n{e}"
                )
        else:
            metadata = {}

        try:
            capacity = self.__extract_max_link_capacity(metadata=metadata)
        except ParsingError as e:
            raise ParsingError(f'Error in line "{line}":\n' + f"{e}")

        return Connection(
            capacity=capacity,
            nodes=[
                next(hub for hub in available_hubs if hub.name == hub1_name),
                next(hub for hub in available_hubs if hub.name == hub2_name),
            ],
        )

    def __filter_lines(self, lines: List[str], prefix: str) -> List[str]:
        """Keep the lines starting with a prefix.

        Args:
            lines: Lines to filter.
            prefix: Prefix to look for.

        Returns:
            The matching lines.
        """
        return [line for line in lines if line.startswith(prefix)]

    def __get_nb_drones_line(self, lines: List[str]) -> str:
        """Find the nb_drones line.

        Args:
            lines: Lines of the map.

        Returns:
            The nb_drones line.

        Raises:
            ParsingError: If there is not exactly one nb_drones line.
        """
        filtered = self.__filter_lines(lines, "nb_drones: ")
        if len(filtered) < 1:
            raise ParsingError("File misses a nb_drones line")
        if len(filtered) > 1:
            raise ParsingError("File has > 1 nb_drones lines")
        return filtered[0]

    def __strip_line(self, line: str) -> str:
        """Remove the comment and surrounding whitespace of a line.

        Args:
            line: Raw line.

        Returns:
            The stripped line.
        """
        if "#" not in line:
            return line.strip()
        return line[: line.index("#")].strip()

    def __strip_lines(self, lines: List[str]) -> List[str]:
        """Strip every line and drop the empty ones.

        Args:
            lines: Raw lines.

        Returns:
            The non-empty stripped lines.
        """
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

    def __normalize_coordinates(self, nodes: List[Node]) -> None:
        """Shift the coordinates so the minimum x and y are 0.

        Args:
            nodes: Zones to shift, modified in place.
        """
        min_x = min(nodes, key=lambda node: node.x).x
        min_y = min(nodes, key=lambda node: node.y).y
        for node in nodes:
            node.x -= min_x
            node.y -= min_y

    def parse(self, map_content: str) -> Map:
        """Parse the content of a map file.

        Args:
            map_content: Content of the map file.

        Returns:
            The parsed map, with its zones, connections and drones.

        Raises:
            ParsingError: If the map is invalid, with the line and the cause.
        """
        try:
            lines = self.__strip_lines(map_content.split("\n"))

            if len(lines) == 0:
                raise ParsingError("Empty map file")
            if not lines[0].startswith("nb_drones:"):
                raise ParsingError(
                    f'Error in line "{lines[0]}":\n'
                    + "First line must be nb_drones"
                )
            if not lines[0].startswith("nb_drones: "):
                raise ParsingError(
                    f'Error in line: "{lines[0]}":\n'
                    + "Missing space after \"nb_drones:\""
                )
            nb_drones = self.__parse_nb_drones(
                self.__get_nb_drones_line(lines)
            )
            entry_point: Optional[Node] = None
            exit_point: Optional[Node] = None
            nodes: List[Node] = []
            node_names: List[str] = []
            connections: List[Connection] = []
            for line in lines[1:]:
                try:
                    if line.startswith("start_hub:"):
                        if not line.startswith("start_hub: "):
                            raise ParsingError(
                                f'Error in line: "{line}":\n'
                                + "Missing space after \"start_hub:\""
                            )
                        if entry_point is not None:
                            raise ParsingError(
                                "File must only contain one start_hub"
                            )
                        entry_point = self.__parse_start_hub(line)
                        if (
                            entry_point.priority == NodePriority.blocked.value
                        ):
                            raise ParsingError(
                                f"Error in line: \"{line}\":\n"
                                + "start_hub cannot be blocked"
                            )
                        nodes.append(entry_point)
                        if entry_point.name in node_names:
                            raise ParsingError(
                                f'Error in line: "{line}":\n'
                                + f"duplicated node name {entry_point.name}"
                            )
                        node_names.append(entry_point.name)
                    elif line.startswith("end_hub:"):
                        if not line.startswith("end_hub: "):
                            raise ParsingError(
                                f'Error in line: "{line}":\n'
                                + "Missing space after \"end_hub:\""
                            )
                        if exit_point is not None:
                            raise ParsingError(
                                "File must only contain one end_hub"
                            )
                        exit_point = self.__parse_end_hub(line)
                        if (
                            exit_point.priority == NodePriority.blocked.value
                        ):
                            raise ParsingError(
                                f"Error in line: \"{line}\":\n"
                                + "end_hub cannot be blocked"
                            )
                        nodes.append(exit_point)
                        if exit_point.name in node_names:
                            raise ParsingError(
                                f'Error in line: "{line}":\n'
                                + f"duplicated node name {exit_point.name}"
                            )
                        node_names.append(exit_point.name)
                    elif line.startswith("hub:"):
                        if not line.startswith("hub: "):
                            raise ParsingError(
                                f'Error in line: "{line}":\n'
                                + "Missing space after \"hub:\""
                            )
                        node = self.__parse_hub(line=line)
                        nodes.append(node)
                        if node.name in node_names:
                            raise ParsingError(
                                f'Error in line: "{line}":\n'
                                + f"duplicated node name {node.name}"
                            )
                        node_names.append(node.name)
                    elif line.startswith("connection:"):
                        if not line.startswith("connection: "):
                            raise ParsingError(
                                f'Error in line: "{line}":\n'
                                + "Missing space after \"connection:\""
                            )
                        known_nodes = list(nodes)
                        connection = self.__parse_connection(line, known_nodes)
                        names = [node.name for node in connection.nodes]
                        for known_connection in connections:
                            if all(
                                new_node.name in names
                                for new_node in known_connection.nodes
                            ):
                                raise ParsingError(
                                    f'Error in line "{line}":\n'
                                    + "Duplicated connection:"
                                    + f"{connection.nodes[0].name}"
                                    + f"-{connection.nodes[1].name}"
                                )
                        for node in connection.nodes:
                            node.connections.append(connection)
                        connections.append(connection)
                    else:
                        line_prefix: str
                        if ":" in line:
                            line_prefix = line[:line.index(':')]
                        elif " " in line:
                            line_prefix = line[:line.index(' ')]
                        else:
                            line_prefix = line
                        raise ParsingError(
                            f'Error in line "{line}":\n'
                            + f"Invalid line prefix \"{
                                line_prefix
                            }\""
                        )
                except ParsingError:
                    raise
                except Exception as e:  # noqa: BLE001
                    raise ParsingError(
                        "An unhandled error occured while parsing"
                        + f'line: "{line}":\n'
                        + f"{e}"
                    )

            if entry_point is None:
                raise ParsingError("Missing start hub")
            if exit_point is None:
                raise ParsingError("Missing end hub")
            if len(connections) == 0:
                raise ParsingError("No connections in map")

            self.__normalize_coordinates(nodes)

            drones: List[Drone] = []

            entry_point.drones_count = nb_drones
            for i in range(nb_drones):
                drone = Drone(id=i + 1, name=f"D{i + 1}")
                drones.append(drone)

            for node in nodes:
                node.connections.sort(
                    key=lambda connection: -next(
                        iter(
                            connected_node
                            for connected_node in connection.nodes
                            if connected_node != node
                        )
                    ).priority
                )

            return Map(
                nb_drones=nb_drones,
                entry_point=entry_point,
                exit_point=exit_point,
                nodes=nodes,
                connections=connections,
                drones=drones,
            )
        except AssertionError as e:
            raise ParsingError(e)
