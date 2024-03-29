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
import java.util.Properties;

/**
 * A class that provides methods for searching using a Python API.
 */
public class PythonAPISearch {

    private static final String PYTHON_API_URL;

    static {
        // load the properties file
        Properties properties = new Properties();
        try {
            properties.load(PythonAPISearch.class.getClassLoader().getResourceAsStream("application.properties"));
            PYTHON_API_URL = properties.getProperty("python.api.url");
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    /**
     * Searches for IDs based on the given query.
     *
     * @param query the search query
     * @return a list of search IDs
     * @throws RuntimeException if an error occurs during the search
     */
    public static List<Integer> searchIds(String query) {
        HttpClient client = HttpClient.newHttpClient();
        String encodedQuery = null;

        query = query.replaceAll("\\/", " ");

        encodedQuery = URLEncoder.encode(query, StandardCharsets.UTF_8)
                .replaceAll("\\+", "%20")
                .replaceAll("\\\\", "%5C");

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

    /**
     * Retrieves a list of alternative queries based on the given query.
     *
     * @param query the search query
     * @return a list of alternative queries
     * @throws RuntimeException if an error occurs during the retrieval of alternative queries
     */
    public static List<String> alternativeQueries(String query) {
        HttpClient client = HttpClient.newHttpClient();
        String encodedQuery = null;

        encodedQuery = URLEncoder.encode(query, StandardCharsets.UTF_8).replaceAll("\\+", "%20");

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(PYTHON_API_URL + "alternate_queries/" + encodedQuery))
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
            return convertJSONToStringIdList(body);
        } else {
            return null;
        }
    }

    /**
     * Converts a JSON string to a list of integers.
     *
     * @param body the JSON string
     * @return a list of integers
     * @throws RuntimeException if an error occurs during the conversion
     */
    private static List<Integer> convertJSONToIdList(String body) {
        ObjectMapper mapper = new ObjectMapper();
        try {
            return Arrays.asList(mapper.readValue(body, Integer[].class));
        } catch (JsonProcessingException e) {
            throw new RuntimeException(e);
        }
    }

    /**
     * Converts a JSON string to a list of strings.
     *
     * @param body the JSON string
     * @return a list of strings
     * @throws RuntimeException if an error occurs during the conversion
     */
    private static List<String> convertJSONToStringIdList(String body) {
        ObjectMapper mapper = new ObjectMapper();
        try {
            return Arrays.asList(mapper.readValue(body, String[].class));
        } catch (JsonProcessingException e) {
            throw new RuntimeException(e);
        }
    }
}
