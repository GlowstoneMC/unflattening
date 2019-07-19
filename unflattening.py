import sys
import json
from collections import OrderedDict

import templates


def _indent(amount, text: str):
    return "\n".join(((" " * amount) + line for line in text.split("\n")))


def flatten_props(props):
    return {key: "/".join(val) for key, val in props.items()}


def to_bukkit_material_enum(name):
    return name.lower()[10:].upper()


def make_java_class(package="net.glowstone.block.flattening.generated", class_name="GeneratedFlatteningData",
                    header="THIS FILE IS GENERATED. DO NOT EDIT DIRECTLY."):
    class_content = ""
    static_content = ""
    imports = (
        "com.google.common.collect.ImmutableBiMap",
        "com.google.common.collect.ImmutableMap",
        "com.google.common.collect.Iterators",
        "java.io.InputStreamReader",
        "java.util.Arrays",
        "java.util.ArrayList",
        "java.util.Arrays",
        "java.util.Iterator",
        "java.util.List",
        "java.util.Map",
        "org.apache.commons.lang.ArrayUtils",
        "org.bukkit.Material",
        "org.bukkit.block.BlockFace",
        "org.bukkit.configuration.file.YamlConfiguration",
    )

    # parse the data
    data = load_data()
    block_faces = OrderedDict()
    properties = OrderedDict()
    state_base_ids = list()
    mat_ids = OrderedDict()
    for block_type in data.keys():
        block = data[block_type]
        mat = to_bukkit_material_enum(block_type)
        if "properties" in block:
            props = block["properties"]
            properties[mat] = props
            if "facing" in props:
                block_faces[mat] = props["facing"]
        else:
            properties[mat] = {}
        base_id = block["states"][0]["id"]
        mat_ids[mat] = base_id
        for state in block["states"]:
            state_base_ids.append(base_id)

    # write the java file
    def _props_map(props):
        return ", ".join((
            "\"{key}\", new PropertyEnum({values})".format(key=key,
                                                           values=", ".join(("\"" + value + "\"" for value in values)))
            for key, values in props.items()
        ))

    class_content += templates.MATERIAL_PROPERTIES_CLASS
    static_content += templates.MATERIAL_PROPERTIES_STATIC.format(
        put_statements=_indent(4, "\n".join((
            ".put(Material.{mat}, "
            "new PropertyDefs(propMapOf({props})))".format(
                mat=mat,
                props=_props_map(props))
            for mat, props in properties.items()
        )))
    )

    class_content += templates.DIRECTIONAL_POSSIBLE_FACES_CLASS
    static_content += templates.DIRECTIONAL_POSSIBLE_FACES_STATIC.format(
        put_statements=_indent(4, "\n".join((
            ".put(Material.{mat}, Arrays.asList({faces}))".format(
                mat=mat,
                faces=", ".join(
                    ("BlockFace." + face.upper() for face in
                     faces)))
            for mat, faces in block_faces.items()
        )))
    )

    class_content += templates.STATE_BASE_IDS_CLASS.format(ids_length=len(state_base_ids))
    static_content += templates.STATE_BASE_IDS_STATIC

    yml_output = templates.STATE_BASE_IDS_YML.format(
        ids=", ".join(
            (str(state) for idx, state in enumerate(state_base_ids))
        ))

    class_content += templates.MATERIAL_ID_MAP_CLASS
    static_content += templates.MATERIAL_ID_MAP_STATIC.format(
        put_statements=_indent(4, "\n".join((
            ".put({base_id}, Material.{mat})".format(
                base_id=base_id,
                mat=mat
            )
            for mat, base_id in mat_ids.items()
        )))
    )

    # output
    return (templates.JAVA_FILE.format(
        header=templates.JAVA_HEADER.format(header=header),
        package=package,
        class_name=class_name,
        class_content=_indent(4, class_content),
        static_content=_indent(8, static_content),
        imports="\n".join(("import " + clazz + ";" for clazz in imports))
    ), yml_output)


def load_data(path="generated/reports/blocks.json") -> dict:
    with open(path) as file:
        return json.load(file)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "--yml":
        print(make_java_class()[1])
    else:
        print(make_java_class()[0])

