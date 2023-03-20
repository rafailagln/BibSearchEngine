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
import java.util.Arrays;
import java.util.List;

public class PythonAPISearch {

    private static final String PYTHON_API_URL = "http://127.0.0.1:5000/search/";

    public static List<SearchResult> search(String query) {

        HttpClient client = HttpClient.newHttpClient();

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(PYTHON_API_URL + query.replaceAll(" ", "%20")))
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
            String title = articleNode.get("title").get(0).asText();
            // Display only the first 10 words of the title
            if(title.split("\\s+").length > 10) {
                title = String.join(" ", Arrays.copyOfRange(title.split("\\s+"), 0, 10)) + "...";
            }
            JsonNode _abstract = articleNode.get("abstract");
            String snippet = _abstract != null ? _abstract.asText() : "";
            if(snippet.split("\\s+").length > 70) {
                snippet = removeHtmlTags(String.join(" ", Arrays.copyOfRange(snippet.split("\\s+"), 0, 70)) + "...");
            }
            String url = articleNode.get("URL").asText();
            results.add(new SearchResult(title, url, snippet));
        }
        return results;
    }

    public static String removeHtmlTags(String htmlText) {
        // Regular expression to match HTML tags
        String regex = "<[^>]*>";

        // Remove all HTML tags
        String plainText = htmlText.replaceAll(regex, " ");

        return plainText;
    }



}
