import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

public class JsonToHashMapExtractor {

    public static Map<String, Object> extract(JsonNode node) {
        Map<String, Object> resultMap = new HashMap<>();
        
        Iterator<Map.Entry<String, JsonNode>> fieldsIterator = node.fields();
        while (fieldsIterator.hasNext()) {
            Map.Entry<String, JsonNode> field = fieldsIterator.next();
            String key = field.getKey();
            JsonNode value = field.getValue();
            if (value.isObject()) {
                resultMap.put(key, extract(value));
            } else if (value.isArray()) {
                resultMap.put(key, extractArray(value));
            } else {
                resultMap.put(key, extractValue(value));
            }
        }
        
        return resultMap;
    }

    private static Object extractValue(JsonNode value) {
        if (value.isTextual()) {
            return value.asText();
        } else if (value.isBoolean()) {
            return value.asBoolean();
        } else if (value.isInt()) {
            return value.asInt();
        } else if (value.isLong()) {
            return value.asLong();
        } else if (value.isDouble()) {
            return value.asDouble();
        } else {
            return value.asText();
        }
    }

    private static Object[] extractArray(JsonNode arrayNode) {
        Object[] array = new Object[arrayNode.size()];
        for (int i = 0; i < arrayNode.size(); i++) {
            JsonNode element = arrayNode.get(i);
            if (element.isObject()) {
                array[i] = extract(element);
            } else if (element.isArray()) {
                array[i] = extractArray(element);
            } else {
                array[i] = extractValue(element);
            }
        }
        return array;
    }

    public static void main(String[] args) throws IOException {
        String jsonString = "{\"name\":\"John\",\"age\":30,\"address\":{\"city\":\"New York\",\"country\":\"USA\"},\"tags\":[\"tag1\",\"tag2\"]}";
        ObjectMapper mapper = new ObjectMapper();
        JsonNode jsonNode = mapper.readTree(jsonString);
        Map<String, Object> resultMap = extract(jsonNode);
        System.out.println(resultMap);
    }
}