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
        "com.google.common.collect.ImmutableMap",
        "java.util.Arrays",
        "java.util.List",
        "org.bukkit.Material",
        "org.bukkit.block.BlockFace",
    )

    # parse the data
    data = load_data()
    block_faces = OrderedDict()
    for block_type in data.keys():
        block = data[block_type]
        if "properties" in block:
            props = block["properties"]
            if "facing" in props:
                block_faces[to_bukkit_material_enum(block_type)] = props["facing"]

    # write the java file
    class_content += templates.DIRECTIONAL_POSSIBLE_FACES_CLASS
    static_content += templates.DIRECTIONAL_POSSIBLE_FACES_STATIC\
        .format(
            put_statements=_indent(4, "\n".join((
                ".put(Material.{mat}, Arrays.asList({faces}))".format(mat=mat,
                                                                      faces=", ".join(
                                                                          ("BlockFace." + face.upper() for face in
                                                                           faces)))
                for mat, faces in block_faces.items()
            )))
        )

    # output
    return templates.JAVA_FILE.format(
        header=templates.JAVA_HEADER.format(header=header),
        package=package,
        class_name=class_name,
        class_content=_indent(4, class_content),
        static_content=_indent(8, static_content),
        imports="\n".join(("import " + clazz + ";" for clazz in imports))
    )


def load_data(path="reports/blocks.json") -> dict:
    with open(path) as file:
        return json.load(file)


if __name__ == '__main__':
    print(make_java_class())
