package org.sample.bibsearchengine.api;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.sample.bibsearchengine.search.SearchResult;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.ArrayList;
import java.util.List;

public class PythonAPISearch {

    private static final String PYTHON_API_URL = "http://localhost:5000/search/";

    public static List<SearchResult> search(String query) {

        HttpClient client = HttpClient.newHttpClient();

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(PYTHON_API_URL + query))
                .GET()
                .build();

        HttpResponse<String> response;
        try {
            response = client.send(request, HttpResponse.BodyHandlers.ofString());
        } catch (IOException | InterruptedException e) {
            throw new RuntimeException(e);
        }

        int statusCode = response.statusCode();
        if (statusCode == 200) {
            String body = response.body();
            // Handle the response body here
            return convertJSONToList(body);
        } else {
            return null;
        }
    }

    private static List<SearchResult> convertJSONToList(String body) {
        ObjectMapper mapper = new ObjectMapper();
        // Parse the JSON string into a JsonNode object
        JsonNode jsonNode;
        try {
            jsonNode = mapper.readTree(body);
        } catch (JsonProcessingException e) {
            throw new RuntimeException(e);
        }
        List<SearchResult> results = new ArrayList<>();
        // Loop through the array of JSON objects and extract the values
        for (JsonNode articleNode : jsonNode) {
            String title = articleNode.get("title").asText();
            String snippet = articleNode.get("snippet").asText();
            String url = articleNode.get("url").asText();
            results.add(new SearchResult(title, url, snippet));
        }
        return results;
    }
}
