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

MATERIAL_PROPERTIES_CLASS = \
"""static final ImmutableMap<Material, PropertyDefs> MATERIAL_PROPERTIES;

static class PropertyDefs {
    private final PropMap properties;

    PropertyDefs(PropMap properties) {
        this.properties = properties;
    }

    public int serialize(Map<String, Object> values) {
        if (values == null) {
            return 0;
        }
        int mask = 0;
        for (int i = this.properties.keys.length - 1; i >= 0; i--) {
            String key = this.properties.keys[i];
            PropertyEnum propEnum = this.properties.enums[i];
            mask |= propEnum.serialize(values.getOrDefault(key, propEnum.defaultValue())) << i;
        }
        return mask;
    }

    public Map<String, Object> deserialize(int serial) {
        int sizeAcc = 0;
        ImmutableMap.Builder<String, Object> result = ImmutableMap.builder();
        for (int i = this.properties.keys.length - 1; i >= 0; i--) {
            String key = this.properties.keys[i];
            PropertyEnum propEnum = this.properties.enums[i];
            int enumSize = (int) Math.ceil(Math.log(propEnum.size()) / Math.log(2));
            int x = ((1 << enumSize) - 1) & (serial >> ((sizeAcc + 1) - 1));
            sizeAcc += enumSize;
            result.put(key, propEnum.deserialize(x));
        }
        return result.build();
    }
}

static class PropertyEnum {
    private final String[] values;

    public PropertyEnum(String... values) {
        this.values = values;
    }

    public int serialize(Object value) {
        return ArrayUtils.indexOf(values, value);
    }

    public Object deserialize(int serial) {
        return values[serial];
    }

    public Object defaultValue() {
        return values[0];
    }

    public int size() {
        return values.length;
    }
}

static class PropertyEnumBoolean extends PropertyEnum {
    public PropertyEnumBoolean() {
        super();
    }

    @Override
    public Object deserialize(int serial) {
        return serial != 1;
    }

    @Override
    public int serialize(Object value) {
        boolean b;
        if (value instanceof Boolean) {
            b = (Boolean) value;
        } else if (value instanceof String) {
            b = Boolean.valueOf((String) value);
        } else {
            b = true;
        }
        return b ? 0 : 1;
    }

    @Override
    public int size() {
        return 2;
    }

    @Override
    public Object defaultValue() {
        return true;
    }
}

static class PropMap {
    private final String[] keys;
    private final PropertyEnum[] enums;

    public PropMap(String[] keys, PropertyEnum[] enums) {
        this.keys = keys;
        this.enums = enums;
    }
}

private static PropMap propMapOf(Object... keysAndVals) {
    Iterator<Object> iter = Iterators.forArray(keysAndVals);
    List<String> keys = new ArrayList<>();
    List<PropertyEnum> enums = new ArrayList<>();
    while (iter.hasNext()) {
        keys.add((String) iter.next());
        enums.add((PropertyEnum) iter.next());
    }
    return new PropMap(keys.toArray(new String[0]), enums.toArray(new PropertyEnum[0]));
}

"""

MATERIAL_PROPERTIES_STATIC = \
"""ImmutableMap.Builder<Material, PropertyDefs> materialPropertiesBuilder = ImmutableMap.builder();
materialPropertiesBuilder
{put_statements}
;
MATERIAL_PROPERTIES = materialPropertiesBuilder.build();
"""


DIRECTIONAL_POSSIBLE_FACES_CLASS = "static final ImmutableMap<Material, List<BlockFace>> " \
                                   "DIRECTIONAL_POSSIBLE_FACES;\n"

DIRECTIONAL_POSSIBLE_FACES_STATIC = \
"""ImmutableMap.Builder<Material, List<BlockFace>> possibleFacesBuilder = ImmutableMap.builder();
possibleFacesBuilder
{put_statements}
;
DIRECTIONAL_POSSIBLE_FACES = possibleFacesBuilder.build();
"""

STATE_BASE_IDS_YML = \
"""
stateBaseIds: [{base_ids}]
stateDefaultIds: [{default_ids}]
"""

STATE_BASE_IDS_STATIC = \
"""
YamlConfiguration stateIdsYml = YamlConfiguration.loadConfiguration(new InputStreamReader(GeneratedFlatteningData.class.getClassLoader().getResourceAsStream("builtin/baseIds.yml")));
stateIdsYml.getIntegerList("stateBaseIds").toArray(STATE_BASE_IDS);
stateIdsYml.getIntegerList("stateDefaultIds").toArray(STATE_DEFAULT_IDS);
"""

STATE_BASE_IDS_CLASS = \
"""
static final Integer[] STATE_BASE_IDS = new Integer[{ids_length}];
static final Integer[] STATE_DEFAULT_IDS = new Integer[{ids_length}];
"""

MATERIAL_ID_MAP_CLASS = \
"""
static final ImmutableBiMap<Integer, Material> MATERIAL_ID_MAP;
"""

MATERIAL_ID_MAP_STATIC = \
"""ImmutableBiMap.Builder<Integer, Material> materialIdMapBuilder = ImmutableBiMap.builder();
materialIdMapBuilder
{put_statements}
;
MATERIAL_ID_MAP = materialIdMapBuilder.build();
"""
