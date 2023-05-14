package org.sample.bibsearchengine.api;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.List;

public class PythonAPISearch {

    private static final String PYTHON_API_URL = "http://127.0.0.1:5000/";

    public static List<Integer> searchIds(String query) {

        HttpClient client = HttpClient.newHttpClient();
        String encodedQuery = null;

        encodedQuery = URLEncoder.encode(query, StandardCharsets.UTF_8).replaceAll("\\+", "%20");

        System.out.println("encodedQuery: " + encodedQuery);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(PYTHON_API_URL + "search_ids/" + encodedQuery))
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
            return convertJSONToIdList(body);
        } else {
            return null;
        }
    }

    private static List<Integer> convertJSONToIdList(String body) {
        ObjectMapper mapper = new ObjectMapper();
        try {
            return Arrays.asList(mapper.readValue(body, Integer[].class));
        } catch (JsonProcessingException e) {
            throw new RuntimeException(e);
        }
    }
}
