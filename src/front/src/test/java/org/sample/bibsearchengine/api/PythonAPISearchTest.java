package org.sample.bibsearchengine.api;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import org.mockito.MockedStatic;
import org.mockito.Mockito;

import java.io.IOException;
import java.net.http.HttpClient;
import java.net.http.HttpResponse;
import java.net.http.HttpRequest;
import java.util.Arrays;
import java.util.List;

/**
 * The type Python api search test.
 */
class PythonAPISearchTest {

    /**
     * Test search ids.
     *
     * @throws Exception the exception
     */
    @Test
    void testSearchIds() throws Exception {
        String query = "test_query";
        String jsonResponse = "[1,2,3]";
        List<Integer> expectedList = Arrays.asList(1,2,3);

        HttpResponse<String> mockedResponse = Mockito.mock(HttpResponse.class);
        Mockito.when(mockedResponse.body()).thenReturn(jsonResponse);
        Mockito.when(mockedResponse.statusCode()).thenReturn(200);

        HttpClient httpClient = Mockito.mock(HttpClient.class);
        Mockito.when(httpClient.send(Mockito.any(HttpRequest.class), Mockito.any(HttpResponse.BodyHandler.class))).thenReturn(mockedResponse);

        try (MockedStatic<HttpClient> httpClientMockedStatic = Mockito.mockStatic(HttpClient.class)) {
            httpClientMockedStatic.when(HttpClient::newHttpClient).thenReturn(httpClient);
            List<Integer> result = PythonAPISearch.searchIds(query);
            assertEquals(expectedList, result);
        }
    }

    /**
     * Test search ids error.
     *
     * @throws Exception the exception
     */
    @Test
    void testSearchIdsError() throws Exception {
        String query = "test_query";

        HttpClient httpClient = Mockito.mock(HttpClient.class);
        Mockito.when(httpClient.send(Mockito.any(HttpRequest.class), Mockito.any(HttpResponse.BodyHandler.class))).thenThrow(IOException.class);

        try (MockedStatic<HttpClient> httpClientMockedStatic = Mockito.mockStatic(HttpClient.class)) {
            httpClientMockedStatic.when(HttpClient::newHttpClient).thenReturn(httpClient);
            assertThrows(RuntimeException.class, () -> PythonAPISearch.searchIds(query));
        }
    }

    /**
     * Test search ids invalid status code.
     *
     * @throws Exception the exception
     */
    @Test
    void testSearchIdsInvalidStatusCode() throws Exception {
        String query = "test_query";

        HttpResponse<String> mockedResponse = Mockito.mock(HttpResponse.class);
        Mockito.when(mockedResponse.statusCode()).thenReturn(404);

        HttpClient httpClient = Mockito.mock(HttpClient.class);
        Mockito.when(httpClient.send(Mockito.any(HttpRequest.class), Mockito.any(HttpResponse.BodyHandler.class))).thenReturn(mockedResponse);

        try (MockedStatic<HttpClient> httpClientMockedStatic = Mockito.mockStatic(HttpClient.class)) {
            httpClientMockedStatic.when(HttpClient::newHttpClient).thenReturn(httpClient);
            assertNull(PythonAPISearch.searchIds(query));
        }
    }

    /**
     * Test alternative queries.
     *
     * @throws Exception the exception
     */
    @Test
    void testAlternativeQueries() throws Exception {
        String query = "test_query";
        String jsonResponse = "[\"query1\",\"query2\",\"query3\"]";
        List<String> expectedList = Arrays.asList("query1","query2","query3");

        HttpResponse<String> mockedResponse = Mockito.mock(HttpResponse.class);
        Mockito.when(mockedResponse.body()).thenReturn(jsonResponse);
        Mockito.when(mockedResponse.statusCode()).thenReturn(200);

        HttpClient httpClient = Mockito.mock(HttpClient.class);
        Mockito.when(httpClient.send(Mockito.any(HttpRequest.class), Mockito.any(HttpResponse.BodyHandler.class))).thenReturn(mockedResponse);

        try (MockedStatic<HttpClient> httpClientMockedStatic = Mockito.mockStatic(HttpClient.class)) {
            httpClientMockedStatic.when(HttpClient::newHttpClient).thenReturn(httpClient);
            List<String> result = PythonAPISearch.alternativeQueries(query);
            assertEquals(expectedList, result);
        }
    }

    /**
     * Test alternative queries error.
     *
     * @throws Exception the exception
     */
    @Test
    void testAlternativeQueriesError() throws Exception {
        String query = "test_query";

        HttpClient httpClient = Mockito.mock(HttpClient.class);
        Mockito.when(httpClient.send(Mockito.any(HttpRequest.class), Mockito.any(HttpResponse.BodyHandler.class))).thenThrow(IOException.class);

        try (MockedStatic<HttpClient> httpClientMockedStatic = Mockito.mockStatic(HttpClient.class)) {
            httpClientMockedStatic.when(HttpClient::newHttpClient).thenReturn(httpClient);
            assertThrows(RuntimeException.class, () -> PythonAPISearch.alternativeQueries(query));
        }
    }

    /**
     * Test alternative queries invalid status code.
     *
     * @throws Exception the exception
     */
    @Test
    void testAlternativeQueriesInvalidStatusCode() throws Exception {
        String query = "test_query";

        HttpResponse<String> mockedResponse = Mockito.mock(HttpResponse.class);
        Mockito.when(mockedResponse.statusCode()).thenReturn(404);

        HttpClient httpClient = Mockito.mock(HttpClient.class);
        Mockito.when(httpClient.send(Mockito.any(HttpRequest.class), Mockito.any(HttpResponse.BodyHandler.class))).thenReturn(mockedResponse);

        try (MockedStatic<HttpClient> httpClientMockedStatic = Mockito.mockStatic(HttpClient.class)) {
            httpClientMockedStatic.when(HttpClient::newHttpClient).thenReturn(httpClient);
            assertNull(PythonAPISearch.alternativeQueries(query));
        }
    }
}
