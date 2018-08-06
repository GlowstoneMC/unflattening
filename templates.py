JAVA_FILE = """{header}
package {package};

{imports}

@Deprecated
public class {class_name} {{
{class_content}

    static {{
{static_content}
    }}
}}
"""

JAVA_HEADER = """/*
 * {header}
 */
"""

DIRECTIONAL_POSSIBLE_FACES_CLASS = "static final ImmutableMap<Material, List<BlockFace>> " \
                                   "DIRECTIONAL_POSSIBLE_FACES;\n"

DIRECTIONAL_POSSIBLE_FACES_STATIC = """ImmutableMap.Builder<Material, List<BlockFace>> possibleFacesBuilder """ \
"""= ImmutableMap.builder();
possibleFacesBuilder
{put_statements}
;
DIRECTIONAL_POSSIBLE_FACES = possibleFacesBuilder.build();
"""


